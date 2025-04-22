# PED-IA

## Overview

PED-IA is a project designed to assist in decision-making and data visualization for medical encounters. It provides a user-friendly interface for exploring hierarchical relationships between medical classes and their contexts, as well as managing encounters and decisions. The project consists of both frontend and backend components, working together to deliver a seamless experience.
PED-IA was developed to support pediatric call center regulation, where non-specialist operators must quickly assess situations and identify appropriate actions. Its primary objective is to:
- Structure the interrogation logic by suggesting clinically relevant questions.
- Highlight contextual information essential to medical decision-making.
- Propose the most critical decision based on collected symptoms and contextual factors.

This is achieved through an ontology-based reasoning system that mirrors the logic of clinical guidelines and expert reasoning. 
By navigating through subclasses, contextual links, and recommended investigations, the user progressively builds a clinical picture, which is then matched with decisions of increasing specificity and severity. This workflow ensures consistency, transparency, and adaptability in triage and decision support.

## Frontend

The frontend is built using **Vue 3** with **Vite** as the build tool. It leverages **Pinia** for state management and **Fretch** for API communication. The user interface is styled with CSS and is designed to be responsive and intuitive. Key features include:

- Interactive visualization of medical classes and their relationships.
- Management of encounters and decisions.
- Integration with backend APIs for real-time data fetching and updates.

### Technologies Used

- **Vue 3**: A progressive JavaScript framework for building user interfaces.
- **Vite**: A fast build tool for modern web development.
- **Pinia**: A state management library for Vue applications.
- **CSS**: For styling and responsive design.

### Setup Instructions

1. Navigate to the `PedIA_front` directory:
   ```bash
   cd PedIA_front
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Backend

The backend is implemented using **Flask** on **AWS Lambda** and **API Gateway** to provide serverless API endpoints. It handles the business logic, data processing, and communication with the frontend. Key features include:

- Fetching and processing hierarchical class data.
- Managing encounter states (in dynamoDB and cookies) and decisions.
- Secure and scalable serverless architecture.
Ontology-based Reasoning

For each class in the ontology, the system dynamically presents the following related elements to the user:

- Subclasses: Immediate children of the class.
- Contextual Classes (aPourContexte): Classes that, when present in the patient's context, influence decisions.
- Related Classes (faitRechercher): Classes that should be actively searched for in the patient's history or examination.

These relationships are extracted from the restrictions defined on each class in the ontology.
This structure enables the system to guide the user through an interrogation pathway by showing:
- What should be investigated further (faitRechercher), and
- What contextual elements might lead to a decision (aPourContexte).

#Avoiding Redundancy

The backend tracks the concepts already presented during an encounter (displayed_classes) to avoid proposing the same concept multiple times. 
When a concept is removed, its subclasses, context-linked classes, and related classes are also removed from the session state to avoid infinite loops or redundant suggestions.

#Decision Logic

There are two types of decisions in the system:

- Contextual Decision (aPourContexte):
A decision class may require specific contextual elements to be valid.
The system evaluates the restrictions associated with the class and verifies whether the required aPourContexte terms are satisfied by the user-selected (clicked_classes) elements.
Logical structures like AND and OR in OWL restrictions are respected during evaluation.

- Direct Decision (aPourDecision):
These are decisions that are directly linked to the selected class and can be proposed without further context.

The backend keeps track of already proposed decisions and always proposes the most severe one according to pre-defined hierarchy.

Users have the ability to remove previously selected classes from the summary of chosen elements (clicked_classes), as during the course of the interrogation, the caregiver or physician might reconsider or correct an earlier assumption. When a class is removed, the system re-evaluates the entire decision logic based on the updated set of selected classes.

### Technologies Used

- **AWS Lambda**: For serverless function execution.
- **API Gateway**: To expose RESTful APIs.
- **Python**: For backend logic and API implementation.

### Setup Instructions

1. Navigate to the `cdk/cdk-python` directory:
   ```bash
   cd cdk/cdk-python
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Deploy the backend infrastructure:
   ```bash
   cdk deploy
   ```

## Project Features

- **Medical Class Visualization**: Explore hierarchical relationships between medical classes, including subclasses, related classes, and context classes.
- **Encounter Management**: Start, manage, and end medical encounters with ease.
- **Decision Support**: Fetch and update decisions based on user interactions.

## Development Tools

- **Visual Studio Code**: Recommended IDE with the Volar extension for Vue 3 development.
- **Vitest**: For unit testing the frontend components.
- **ESLint**: For linting and maintaining code quality.

## Getting Started

Follow the setup instructions for both the frontend and backend to get the project running locally. For more details, refer to the respective README files in the `PedIA_front` and `cdk/cdk-python` directories.
