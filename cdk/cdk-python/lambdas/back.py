import logging
import os

# import redis
# import json
from datetime import timedelta
from time import sleep
from uuid import uuid4

import awsgi
import boto3
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
from owlready2 import *

logging.basicConfig(level=logging.DEBUG)

PedIA = Flask(__name__)
CORS(
    PedIA,
    supports_credentials=True,
    origins=[
        "https://prod.d35d12lv6zuvjs.amplifyapp.com",
    ],
)
# PedIA.secret_key = "447704598de9847be546a7b32055a611bc8e875f2dde59f31222752f3ef8bead"
# PedIA.config["SESSION_TYPE"] = "dynamodb"
# PedIA.config["SESSION_COOKIE_NAME"] = "session"
# PedIA.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
dynamodb = boto3.resource("dynamodb")
# PedIA.config["SESSION_DYNAMODB"] = dynamodb
# PedIA.config["SESSION_DYNAMODB_TABLE_NAME"] = "Sessions"

SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='None'

SESSION_TYPE = "dynamodb"
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_DYNAMODB = dynamodb
SESSION_DYNAMODB_TABLE = "Sessions"

PedIA.config.from_object(__name__)

Session(PedIA)


# r = redis.from_url(os.environ.get("REDIS_URL"))

onto = get_ontology("OntoRegulPed.owl").load()


##Conversion des noms de classes en label

label_to_class = {}

for cls in onto.classes():
    if cls.label:
        label_to_class[cls.label.first().lower()] = cls.name

## Début de la session

# session = {}


def handler(event, context):
    return awsgi.response(PedIA, event, context)


@PedIA.route("/start_encounter")
def start_encounter():
    encounter_id = str(uuid4())
    session["encounter_id"] = encounter_id
    session[encounter_id] = {"clicked_classes": [], "parent_classes": {}, "displayed_classes": []}
    return jsonify({"message": "Régulation d'un nouveau patient", "encounter_id": encounter_id})


def push_class_to_session(class_name, encounter_id):
    session[encounter_id]["clicked_classes"].append(class_name)


def push_classes_relatives(class_name, contexts, encounter_id):
    contexts = [label_to_class.get(context["name"].lower(), context["name"]) for context in contexts]
    for context in contexts:
        session[encounter_id]["parent_classes"][context] = class_name


# Gestion  des boucles infinies
@PedIA.route("/remove_displayed_class", methods=["POST"])
def remove_displayed_class():
    data = request.json
    class_name = data.get("class_name")
    label = class_name.lower()
    class_name_onto = label_to_class.get(label, class_name)
    encounter_id = request.get_json(force=True)["encounter_id"]

    if not encounter_id:
        return jsonify({"error": "No active encounter"}), 400

    displayed_classes = set(session.get(encounter_id, {}).get("displayed_classes", set()))
    # print(f"displayed classes : {displayed_classes}")

    if class_name in displayed_classes:
        displayed_classes.remove(class_name)

        # Retrieve subclasses, related classes, and context classes
        subclasses = get_subclasses_for_removal(class_name_onto)
        related_classes = get_classes_after_faitRechercher_for_removal(class_name_onto)
        context_classes = get_classes_after_aPourContexte_for_removal(class_name_onto)

        # Remove each class from the displayed_classes set
        for subclass in subclasses:
            displayed_classes.discard(subclass)
        for related in related_classes:
            displayed_classes.discard(related)
        for context in context_classes:
            displayed_classes.discard(context)

        session[encounter_id]["displayed_classes"] = list(displayed_classes)
        # print(f"displayed classes : {displayed_classes}")
        return jsonify(
            {
                "message": f"Removed {class_name} and related classes from displayed classes",
                "displayed_classes": list(displayed_classes),
            }
        )
    else:
        return jsonify({"error": f"{class_name} not found in displayed classes"}), 404


def get_subclasses_for_removal(class_name):
    try:
        cls = onto.search_one(iri="*" + class_name)
        if cls:
            subclasses = [subclass.label.first() if subclass.label else subclass.name for subclass in cls.subclasses()]
            return subclasses
        else:
            logging.warning(f"No subclasses found for class {class_name}")
            return []
    except Exception as e:
        logging.error(f"Error processing request for {class_name}: {e}")
        return []


def get_classes_after_faitRechercher_for_removal(class_name):
    try:
        cls = onto.search_one(iri="*" + class_name)
        if not cls:
            return []

        related_classes = []
        for element in cls.is_a:
            process_class_element(element, related_classes, set())

        return [related["name"] for related in related_classes]
    except Exception as e:
        logging.error(f"Error processing request for {class_name}: {e}")
        return []


def get_classes_after_aPourContexte_for_removal(class_name):
    try:
        cls = onto.search_one(iri="*" + class_name)
        if not cls:
            return []

        context_groups = []
        for element in cls.is_a:
            result, _ = extract_context(element)
            if result:
                context_groups.extend([item["name"] for item in result])

        return context_groups
    except Exception as e:
        logging.error(f"Error processing request for {class_name}: {e}")
        return []


## Route pour la page d'acceuil : récupère les motifs d'appels


@PedIA.route("/get_motives")
def get_motives():
    try:
        motif_appel = onto.search_one(iri="*MotifAppel")
        if motif_appel:
            subclasses = [
                subclass.label.first() if subclass.label else subclass.name for subclass in motif_appel.subclasses()
            ]
            return jsonify(subclasses)
        else:
            logging.warning("No motifs found for the given IRI")
            return jsonify([]), 404
    except Exception as e:
        logging.error(f"Failed to get motives due to: {e}")
        return jsonify({"error": "Error retrieving motives"}), 500


##########  ROUTES POUR LA PAGE PRINCIPALE DE REGULATION ###################


@PedIA.route("/push_class_to_session", methods=["POST"])
def push_class_to_session_route():
    class_name = request.args.get("class_name")
    label = class_name.lower()
    class_name = label_to_class.get(label, class_name)
    encounter_id = request.get_json(force=True)["encounter_id"]

    push_class_to_session(class_name, encounter_id)

    return jsonify([]), 200


## Récupérer les sous-classes


@PedIA.route("/get_subclasses", methods=["POST"])
def get_subclasses():
    class_name = request.args.get("class_name")
    label = class_name.lower()
    class_name = label_to_class.get(label, class_name)
    encounter_id = request.get_json(force=True)["encounter_id"]

    # push_class_to_session(class_name)

    if not encounter_id:
        return jsonify({"error": "No encounter started"}), 400

    if not class_name:
        return jsonify({"error": f"Class not found for label: {label}"}), 404
    try:
        cls = onto.search_one(iri="*" + class_name)
        if cls:
            subclasses = []
            for subclass in cls.subclasses():
                subclass_name = subclass.label.first() if subclass.label else subclass.name
                if subclass_name not in session[encounter_id]["displayed_classes"]:
                    session[encounter_id]["displayed_classes"].append(subclass_name)
                    subclasses.append({"name": subclass_name, "id": subclass.name})
            return jsonify(subclasses)
        else:
            logging.warning(f"No subclasses found for class {class_name}")
            return jsonify([]), 404
    except Exception as e:
        logging.error(f"Error processing request for {class_name}: {e}")
        return jsonify({"error": "An error occurred fetching subclasses"}), 500


## Récupérer les classes après faitRechercher dans la description de la classe cliquée


@PedIA.route("/get_classes_after_faitRechercher", methods=["POST"])
def get_classes_after_faitRechercher():
    class_name = request.args.get("class_name")
    label = class_name.lower()
    class_name = label_to_class.get(label, class_name)

    if not class_name:
        return jsonify({"error": f"Class not found for label: {class_name}"}), 404

    encounter_id = request.get_json(force=True)["encounter_id"]
    if not encounter_id:
        return jsonify({"error": "No active encounter"}), 400

    cls = onto.search_one(iri="*" + class_name)
    if not cls:
        return jsonify([]), 404

    related_classes = []
    displayed_classes = set(session[encounter_id].get("displayed_classes", set()))
    try:
        for element in cls.is_a:
            element, related_classes, displayed_classes = process_class_element(
                element, related_classes, displayed_classes
            )

        session[encounter_id]["displayed_classes"] = list(displayed_classes)
        return jsonify(related_classes)
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


def process_class_element(element, related_classes, displayed_classes):
    if isinstance(element, Restriction) and element.property == onto.faitRechercher:
        add_related_class(element.value, related_classes, displayed_classes)
    elif isinstance(element, (Or, And)):
        for part in element.Classes:
            if isinstance(part, Restriction) and part.property == onto.faitRechercher:
                add_related_class(part.value, related_classes, displayed_classes)

    return element, related_classes, displayed_classes


def add_related_class(class_instance, related_classes, displayed_classes):
    if isinstance(class_instance, ThingClass):
        class_name = class_instance.label.first() if class_instance.label else class_instance.name
        if class_name not in displayed_classes:
            displayed_classes.add(class_name)
            related_classes.append({"name": class_name})
    return class_instance, related_classes, displayed_classes


## Récupérer les classes après aPourContexte dans la description de la classe cliquée


def extract_context(element):
    results = []
    decision = ""
    if isinstance(element, And) or isinstance(element, Or):
        relation_type = "and" if isinstance(element, And) else "or"
        elements = list(element.Classes)
        for i, part in enumerate(elements):
            part_results, _ = extract_context(part)
            if part_results:
                results.extend(part_results if isinstance(part_results, list) else [part_results])
                if i < len(elements) - 1:
                    results[-1]["relation"] = relation_type
            else:
                decision = part
    elif isinstance(element, Restriction) and element.property == onto.aPourContexte:
        class_name = element.value.label.first() if element.value.label else element.value.name
        results.append({"name": class_name, "relation": None})
    return results, decision


@PedIA.route("/get_classes_after_aPourContexte", methods=["POST"])
def get_classes_after_aPourContexte():
    class_name = request.args.get("class_name")
    label = class_name.lower()
    class_name = label_to_class.get(label, class_name)

    if not class_name:
        return jsonify({"error": f"Class not found for label: {label}"}), 404

    encounter_id = request.get_json(force=True)["encounter_id"]
    if not encounter_id:
        return jsonify({"error": "No active encounter"}), 400

    cls = onto.search_one(iri="*" + class_name)
    if not cls:
        return jsonify([]), 404

    try:
        context_groups = []
        for element in cls.is_a:
            result, _ = extract_context(element)
            if result:
                for item in result:
                    context_name = item["name"]
                    if context_name not in session[encounter_id]["displayed_classes"]:
                        session[encounter_id]["displayed_classes"].append(context_name)
                        context_groups.append(item)
        push_classes_relatives(class_name, context_groups, encounter_id)
        return jsonify(context_groups)
    except Exception as e:
        logging.exception("Failed to process /get_classes_after_aPourContexte")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


###### MODULE DE DECISION #########


# S'assurer d'avoir la "pire" décision

decision_rankings = {"R1": 1, "R2A": 2, "R2B": 3, "R3": 4, "R4": 5}


def get_decision_severity(decision_name):
    return decision_rankings.get(decision_name, float("inf"))


# Fonction pour gérer les décisions contextuelles (selon les classes de aPourContexte qui ont été cliquées)


def handle_context(element, clicked_classes):
    if isinstance(element, And):
        results = all(
            handle_context(sub_elem, clicked_classes) for sub_elem in element.Classes if not is_decision(sub_elem)
        )
        print(f"Evaluating AND: {results}")
        return results
    elif isinstance(element, Or):
        results = any(
            handle_context(sub_elem, clicked_classes) for sub_elem in element.Classes if not is_decision(sub_elem)
        )
        print(f"Evaluating OR: {results}")
        return results
    elif isinstance(element, Restriction) and element.property == onto.aPourContexte:
        result = element.value.name in clicked_classes
        print(f"Checking if {element.value.name} is in {clicked_classes}: {result}")
        return result
    else:
        return False


def is_decision(element):
    return isinstance(element, Restriction) and element.property == onto.aPourDecisionRegulation


# Route pour récupérer la décision


@PedIA.route("/get_decision", methods=["POST"])
def get_decision():
    data = request.get_json(force=True)
    class_name = data["class_name"]
    label = class_name.lower()
    class_name = label_to_class.get(label, class_name)

    if not class_name:
        return jsonify({"error": f"Class not found for label: {label}"}), 404
    encounter_id = data["encounter_id"]
    if not encounter_id:
        return jsonify({"error": "No encounter started"}), 400

    print(f"Searching for class with IRI ending in {class_name}")
    cls = onto.search_one(iri="*" + class_name)
    if not cls:
        print(f"Class not found: {class_name}")
        return jsonify({"error": "Class not found"}), 404

    decisions = []
    current_worst = session.get(f"{encounter_id}_worst_decision", "R4")
    clicked_classes = session[encounter_id].get("clicked_classes", [])

    try:
        # Direct decisions
        for element in cls.is_a:
            if isinstance(element, Restriction) and element.property == onto.aPourDecisionRegulation:
                if isinstance(element.value, ThingClass):
                    decision_name = element.value.name
                    decisions.append({"name": decision_name, "type": "direct"})
                    # print({"name": decision_name, "type": "direct"})
                    # Update worst decision if current is more severe
                    if get_decision_severity(decision_name) < get_decision_severity(current_worst):
                        current_worst = decision_name

        # Only proceed to contextual decisions if there were no direct decisions found or based on some other condition
        if not decisions:
            parent_class_name = session[encounter_id]["parent_classes"].get(class_name)
            if parent_class_name:
                parent_cls = onto.search_one(iri="*" + parent_class_name)

                for element in parent_cls.is_a:
                    if isinstance(element, (And, Or, Restriction)):
                        result = handle_context(element, clicked_classes)
                        if result:
                            decision_list = [
                                res
                                for res in element.Classes
                                if isinstance(res, Restriction) and res.property == onto.aPourDecisionRegulation
                            ]
                            if decision_list:
                                decision_name = decision_list[0].value.name
                                decisions.append({"name": decision_name, "type": "contextual"})
                                # print(f"Décision contextuelle : {decision_name}")
                                if get_decision_severity(decision_name) < get_decision_severity(current_worst):
                                    current_worst = decision_name
                                    # print(f"Pire decision retenue : {current_worst}")
            else:
                print(f"No parent class for {class_name}, assumed to be a root or standalone class.")

        # Save the updated worst decision back to the session
        session[f"{encounter_id}_worst_decision"] = current_worst

        return jsonify({"decisions": decisions, "worst_decision": current_worst})
    except Exception as e:
        logging.error(f"Error processing decisions for class {class_name}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


####### SESSION #######

## Fenêtre d'historique des classes cliquées + possibllité de retrait --> si retrait, doit ré-évaluer la décision


@PedIA.route("/get_clicked_classes", methods=["POST"])
def get_clicked_classes():
    encounter_id = request.get_json(force=True)["encounter_id"]

    if not encounter_id:
        return jsonify({"error": "No active encounter"}), 400
    clicked_classes = session[encounter_id].get("clicked_classes", [])
    clicked_class_labels = []
    for cls_name in clicked_classes:
        cls = onto[cls_name]
        if cls:
            label = cls.label.first() if cls.label else cls.name
            clicked_class_labels.append(label)
        else:
            print(f"Class {cls_name} not found in ontology.")
    clicked_class_labels = list(set(clicked_class_labels))
    return jsonify({"clicked_classes": clicked_class_labels})


def get_class_name_from_label_or_name(label_or_name):
    for cls in onto.classes():
        if cls.label and label_or_name in cls.label:
            return cls.name
        elif cls.name == label_or_name:
            return cls.name
    return None


@PedIA.route("/remove_clicked_class", methods=["POST"])
def remove_clicked_class():
    data = request.json
    # print(f"data : {data}")
    label_or_name = data.get("class_name")
    encounter_id = request.get_json(force=True)["encounter_id"]

    if not encounter_id:
        return jsonify({"error": "No active encounter"}), 400

    class_name = get_class_name_from_label_or_name(label_or_name)
    if not class_name:
        return jsonify({"error": f"Class with label or name '{label_or_name}' not found in ontology"}), 404

    if class_name in session[encounter_id]["clicked_classes"]:
        session[encounter_id]["clicked_classes"].remove(class_name)

        # Function to re-fetch decisions
        def fetch_decisions(encounter_id):
            decisions = []
            current_worst = "R4"  # session.get(f'{encounter_id}_worst_decision', 'R4')
            clicked_classes = session[encounter_id].get("clicked_classes", [])
            # print(f"classes cliquées : {clicked_classes}")

            # Iterate over all clicked classes to determine decisions
            for clicked_class in clicked_classes:
                cls = onto.search_one(iri="*" + clicked_class)
                # print(f"cls : {cls}")
                if not cls:
                    continue

                for element in cls.is_a:
                    # print(f"element direct : {element}")
                    if isinstance(element, Restriction) and element.property == onto.aPourDecisionRegulation:
                        if isinstance(element.value, ThingClass):
                            decision_name = element.value.name
                            decisions.append({"name": decision_name, "type": "direct"})
                            # print({"name": decision_name, "type": "direct"})
                            # Update worst decision if current is more severe
                            if get_decision_severity(decision_name) < get_decision_severity(current_worst):
                                current_worst = decision_name

            # If no direct decisions found, move on to contextual decisions
            if not decisions:
                for clicked_class in clicked_classes:
                    # print(f"clicked_class : {clicked_class}")
                    # print(f"praent_classes de la sessions : {session[encounter_id]['parent_classes']}")
                    parent_class_name = session[encounter_id]["parent_classes"].get(clicked_class)
                    # print(f"parent_class_name : {parent_class_name}" )
                    if parent_class_name:
                        parent_cls = onto.search_one(iri="*" + parent_class_name)
                        if not parent_cls:
                            continue
                        for element in parent_cls.is_a:
                            # print(f"element context : {element}")
                            if isinstance(element, (And, Or, Restriction)):
                                result = handle_context(element, clicked_classes)
                                print(f"result : {result}")
                                if result:
                                    decision_list = [
                                        res
                                        for res in element.Classes
                                        if isinstance(res, Restriction) and res.property == onto.aPourDecisionRegulation
                                    ]
                                    if decision_list:
                                        decision_name = decision_list[0].value.name
                                        decisions.append({"name": decision_name, "type": "contextual"})
                                        print({"name": decision_name, "type": "contextuelle"})
                                        if get_decision_severity(decision_name) < get_decision_severity(current_worst):
                                            current_worst = decision_name
                    else:
                        print(f"No parent class for {clicked_class}, assumed to be a root or standalone class.")

            session[f"{encounter_id}_worst_decision"] = current_worst
            return {"decisions": decisions, "worst_decision": current_worst}

        # Re-fetch the decisions
        updated_decisions = fetch_decisions(encounter_id)
        print(f"upadted_decision = {updated_decisions}")

        # logging.info(f"Updated decisions: {updated_decisions}, type: {type(updated_decisions)}")

        if "error" in updated_decisions:
            return jsonify(updated_decisions), 404

        return jsonify(
            {
                "message": f"Removed {class_name} from clicked classes",
                "clicked_classes": session[encounter_id]["clicked_classes"],
                "decisions": updated_decisions["decisions"],
                "worst_decision": updated_decisions["worst_decision"],
            }
        )
    else:
        return jsonify({"error": f"{class_name} not found in clicked classes"}), 404


############ Fin de la session #################


@PedIA.route("/end_encounter", methods=["POST"])
def end_encounter():
    encounter_id = request.get_json(force=True)["encounter_id"]
    if encounter_id:
        encounter_data = session.pop(encounter_id, {})
        if isinstance(encounter_data, dict):
            for key, value in encounter_data.items():
                if isinstance(value, set):
                    encounter_data[key] = list(value)
        return jsonify({"message": "Fin de la régulation du patient", "data": encounter_data})
    return jsonify({"message": "Pas de régulation en cours"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    PedIA.run(host="0.0.0.0", port=port, debug=True)
