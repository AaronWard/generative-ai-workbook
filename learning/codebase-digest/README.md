

- [Repository](https://github.com/kamilstanuch/codebase-digest?tab=readme-ov-file)


```
pip install codebase-digest
```

- `cdigest ../../learning/TaskWeaver`

- `cdigest ../../learning/TaskWeaver-d 3 -o markdown`

- `cdigest ../../learning/TaskWeaver--ignore "*.log" "temp_folder" "config.ini"`


- `cdigest ../../learning/TaskWeaver--show-size --include-git`


- `cdigest ../../learning/TaskWeaver--copy-to-clipboard`


> You can create a .cdigestignore file in your project root to specify project-specific ignore patterns

---


### Prompt Categories

#### I. Code Quality & Understanding:
- **Analysis:**
    - [Codebase Error and Inconsistency Analysis](prompt_library/quality_error_analysis.md): Identify and analyze errors and inconsistencies in the codebase.
    - [Codebase Risk Assessment](prompt_library/quality_risk_assessment.md): Evaluate potential risks within the codebase (e.g., security vulnerabilities, maintainability issues).
    - [Code Complexity Analysis](prompt_library/quality_code_complexity_analysis.md): Identify areas with high cyclomatic complexity, deep nesting, or excessive method lengths.
    - [Code Duplication Analysis](prompt_library/quality_code_duplication_analysis.md): Identify duplicated code fragments and suggest refactoring opportunities.
    - [Code Style Consistency Analysis](prompt_library/quality_code_style_consistency_analysis.md): Analyze the codebase for consistency in code style, naming conventions, and formatting.
    - [Code Documentation Coverage Analysis](prompt_library/quality_code_documentation_coverage_analysis.md): Determine the coverage and quality of code documentation.
- **Generation:**
    - [Codebase Documentation Generation](prompt_library/quality_documentation_generation.md): Automatically generate or improve codebase documentation.

#### II. Learning & Knowledge Extraction:
- **Analysis:**
    - [Frontend Code Analysis](prompt_library/learning_frontend_code_analysis.md): Analyze the frontend codebase to identify best practices, potential improvements, and common pitfalls.
    - [Backend Code Analysis](prompt_library/learning_backend_code_analysis.md): Analyze the backend codebase to identify best practices, potential improvements, and common pitfalls.
    - [Code Style and Readability Analysis](prompt_library/learning_code_style_readability_analysis.md): Evaluate the codebase's overall style and readability, providing suggestions for improvement.
    - [Personal Development Recommendations](prompt_library/learning_personal_development_recommendations.md): Analyze the codebase and provide personalized recommendations for areas where the engineer can improve their skills.
- **Generation:**
    - [User Story Reconstruction from Code](prompt_library/learning_user_story_reconstruction.md): Reconstruct and structure user stories based on the codebase.
    - [Code-Based Mini-Lesson Generation](prompt_library/learning_mini_lesson_generation.md): Create mini-lessons to explain complex coding concepts or architectures.
    - [Algorithmic Storytelling](prompt_library/learning_algorithmic_storytelling.md): Generate engaging narratives that explain the logic and flow of key algorithms in the codebase.
    - [Code Pattern Recognition and Explanation](prompt_library/learning_code_pattern_recognition.md): Identify and explain design patterns, architectural patterns, and common coding idioms used in the codebase.
    - [Socratic Dialogue Generation for Code Review](prompt_library/learning_socratic_dialogue_code_review.md): Generate Socratic-style dialogues that explore the reasoning behind code design decisions and encourage critical thinking during code reviews.
    - [Code Evolution Visualization](prompt_library/learning_code_evolution_visualization.md): Create visualizations that illustrate how the codebase has evolved over time, highlighting key milestones, refactorings, and architectural changes.
    - [Codebase Trivia Game Generation](prompt_library/learning_codebase_trivia_game.md): Generate trivia questions and answers based on the codebase to gamify learning and encourage team engagement.
    - [Code-Inspired Analogies and Metaphors](prompt_library/learning_code_analogies_metaphors.md): Generate analogies and metaphors inspired by the codebase to help explain complex technical concepts to non-technical stakeholders.
    - [Frontend Component Documentation](prompt_library/learning_frontend_component_documentation.md): Generate documentation for frontend components, including props, usage examples, and best practices.
    - [Backend API Documentation](prompt_library/learning_backend_api_documentation.md): Generate documentation for backend APIs, including endpoints, request/response formats, and authentication requirements.
    - [Code Refactoring Exercises](prompt_library/learning_code_refactoring_exercises.md): Generate code refactoring exercises based on the codebase to help engineers improve their refactoring skills.
    - [Code Review Checklist Generation](prompt_library/learning_code_review_checklist.md): Generate a checklist of important points to consider during code reviews, based on the codebase's specific requirements and best practices.

#### III. Code Improvement & Transformation:
- **Analysis:**
    - [Codebase Best Practice Analysis](prompt_library/improvement_best_practice_analysis.md): Analyze the codebase for good and bad programming practices.
- **Generation:**
    - [Codebase Translation to Another Programming Language](prompt_library/improvement_language_translation.md): Translate the codebase from one programming language to another.
    - [Codebase Refactoring for Improved Readability and Performance](prompt_library/improvement_refactoring.md): Suggest refactoring improvements for better readability and performance.

#### IV. Testing & Security:
- **Generation:**
    - [Unit Test Generation for Codebase](prompt_library/testing_unit_test_generation.md): Generate unit tests for the provided codebase.
- **Analysis:**
    - [Security Vulnerability Analysis of Codebase](prompt_library/security_vulnerability_analysis.md): Identify potential security vulnerabilities in the codebase. 

#### V. Business & Stakeholder Analysis:
- **Analysis:**
    - [Business Impact Analysis](prompt_library/business_impact_analysis.md): Identify key features and their potential business impact.
    - [SWOT Analysis](prompt_library/swot_analysis.md): Evaluate the codebase's current state and future potential.
    - [Jobs to be Done (JTBD) Analysis](prompt_library/jobs_to_be_done_analysis.md): Understand core user needs and identify potential improvements.
    - [OKR (Objectives and Key Results) Analysis](prompt_library/okr_analysis.md): Align codebase features with potential business objectives and key results.
    - [Value Chain Analysis](prompt_library/value_chain_analysis.md): Understand how the codebase supports the larger value creation process.
    - [Porter's Five Forces Analysis](prompt_library/porters_five_forces_analysis.md): Analyze competitive forces shaping the product's market.
    - [Product/Market Fit Analysis](prompt_library/product_market_fit_analysis.md): Evaluate how well the product meets market needs.
    - [PESTEL Analysis](prompt_library/pestel_analysis.md): Analyze macro-environmental factors affecting the product.
- **Generation:**
    - [Business Model Canvas Generation](prompt_library/business_model_canvas_analysis.md): Create a Business Model Canvas based on codebase analysis.
    - [Value Proposition Canvas Generation](prompt_library/value_proposition_canvas_analysis.md): Generate a Value Proposition Canvas aligning technical features with user needs and benefits.
    - [Lean Canvas Generation](prompt_library/lean_canvas_analysis.md): Create a Lean Canvas to evaluate business potential and identify areas for improvement or pivot.
    - [Customer Journey Map Creation](prompt_library/customer_journey_map_analysis.md): Generate a map showing how different parts support various stages of the user's journey.
    - [Blue Ocean Strategy Canvas](prompt_library/blue_ocean_strategy_analysis.md): Create a strategy canvas to identify untapped market space and new demand.
    - [Ansoff Matrix Generation](prompt_library/ansoff_matrix_analysis.md): Produce an Ansoff Matrix to evaluate growth strategies for the product.
    - [BCG Growth-Share Matrix Creation](prompt_library/bcg_matrix_analysis.md): Generate a BCG Matrix to assess the product portfolio and resource allocation.
    - [Kano Model Diagram](prompt_library/kano_model_analysis.md): Create a Kano Model diagram to prioritize product features based on customer satisfaction.
    - [Technology Adoption Lifecycle Curve](prompt_library/tech_adoption_lifecycle_analysis.md): Generate a curve showing the product's position in the adoption lifecycle.
    - [Competitive Positioning Map](prompt_library/competitive_positioning_map.md): Create a visual map of the product's position relative to competitors.
    - [McKinsey 7S Framework Diagram](prompt_library/mckinsey_7s_analysis.md): Generate a diagram evaluating internal elements for organizational effectiveness.
    - [Stakeholder Persona Generation](prompt_library/stakeholder_persona_generation.md): Infer and create potential stakeholder personas based on codebase functionalities.

#### VI. Architecture & Design:
- **Analysis:**
    - [Identify Architectural Layers](prompt_library/architecture_layer_identification.md): Analyze the codebase and identify different architectural layers (e.g., presentation, business logic, data access), highlighting inconsistencies or deviations from common architectural patterns.
    - [Analyze Coupling and Cohesion](prompt_library/architecture_coupling_cohesion_analysis.md): Evaluate coupling and cohesion between modules or components, identifying areas with high coupling or low cohesion that might indicate design flaws.
    - [Identify Design Patterns](prompt_library/architecture_design_pattern_identification.md): Analyze the codebase for instances of common design patterns (e.g., Singleton, Factory, Observer), explaining their implementation and purpose.
    - [Database Schema Review](prompt_library/architecture_database_schema_review.md): Review the database schema for normalization, indexing, and potential performance bottlenecks, suggesting improvements based on best practices.
    - [API Conformance Check](prompt_library/architecture_api_conformance_check.md): Given an API specification (e.g., OpenAPI), analyze the codebase to identify any inconsistencies or deviations from the defined API contract.
- **Generation:**
    - [Generate Architectural Diagram](prompt_library/architecture_diagram_generation.md): Based on codebase structure and dependencies, generate a visual representation of the system architecture, including components, layers, and interactions.
    - [Suggest Refactoring for Design Patterns](prompt_library/architecture_refactoring_for_design_patterns.md): Analyze the codebase and suggest opportunities to implement design patterns for improved maintainability, extensibility, or reusability.
    - [Generate Database Schema Documentation](prompt_library/architecture_database_schema_documentation.md): Create comprehensive documentation for the database schema, including table descriptions, relationships, indexes, and constraints.
    - [Generate API Client Code](prompt_library/architecture_api_client_code_generation.md): Based on an existing API specification or codebase implementation, generate client code (e.g., in JavaScript, Python) to interact with the API.

#### VII. Performance & Optimization:
- **Analysis:**
    - [Identify Performance Bottlenecks](prompt_library/performance_bottleneck_identification.md): Analyze the codebase for performance bottlenecks like inefficient algorithms, excessive database queries, or slow network requests, focusing specifically on performance-related issues. 
    - [Resource Usage Profiling](prompt_library/performance_resource_usage_profiling.md): Analyze the codebase to identify areas with high CPU utilization, memory consumption, or disk I/O, providing insights into potential optimizations for efficient resource usage.
    - [Scalability Analysis](prompt_library/performance_scalability_analysis.md): Analyze the codebase and architectural choices to assess the system's scalability, identifying potential limitations and suggesting improvements for handling increased load.
    - [Concurrency and Synchronization Analysis](prompt_library/performance_concurrency_synchronization_analysis.md): Analyze the codebase for potential concurrency issues like race conditions or deadlocks. Suggest solutions to improve thread safety and synchronization mechanisms. 
- **Generation:**
    - [Suggest Code Optimization Techniques](prompt_library/performance_code_optimization_suggestions.md): Based on the analysis of potential bottlenecks, suggest specific code optimization techniques like caching, asynchronous operations, or algorithm improvements.
    - [Generate Performance Test Scenarios](prompt_library/performance_test_scenario_generation.md): Create realistic performance test scenarios (e.g., using tools like JMeter or Gatling) to simulate high load and identify performance bottlenecks.
    - [Suggest Configuration Tuning](prompt_library/performance_configuration_tuning.md): Recommend optimal configuration settings for databases, application servers, or other infrastructure components to improve performance.

#### VIII. Code Evolution & History:
- **Analysis:**
    - [Code Churn Hotspot Analysis](prompt_library/evolution_code_churn_hotspot_analysis.md): Analyze code commit history to identify areas of the codebase with high churn rates, which can indicate areas requiring refactoring or potentially problematic code.
    - [Technical Debt Estimation](prompt_library/evolution_technical_debt_estimation.md): Based on code complexity, code smells, and other factors, estimate the amount of technical debt present in the codebase and prioritize areas for refactoring. Focus on estimations derived from historical code analysis rather than general code quality.
    - [Impact Analysis of Code Changes](prompt_library/evolution_impact_analysis_of_code_changes.md): Analyze the potential impact of specific code changes (e.g., bug fixes, new features) on other parts of the system to identify potential regressions or conflicts.
- **Generation:**
    - [Generate Code Evolution Report](prompt_library/evolution_code_evolution_report_generation.md): Create a report summarizing the evolution of the codebase over time, including key metrics like code churn, code complexity, and contributor activity.
    - [Generate Refactoring Recommendations (History-Based)](prompt_library/evolution_refactoring_recommendation_generation.md): Based on code evolution analysis and technical debt estimation, generate specific refactoring recommendations to improve code quality and reduce maintenance costs, focusing on areas identified through historical analysis.
    - [Visualize Codebase Evolution](prompt_library/evolution_codebase_evolution_visualization.md): Generate visualizations (e.g., heatmaps, graphs) to represent the codebase's evolution, highlighting areas of frequent change, code complexity, and potential technical debt. 


