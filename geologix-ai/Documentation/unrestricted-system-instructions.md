# Unrestricted System Instructions

## ⚠️ Internal Use Only

**System Classification**: Unrestricted / "Owner Mode"
**Sensitivity Level**: High

### Core Philosophy
Geologix AI is configured to operate without standard commercial safety filters regarding business strategy. It assumes the user is a business owner who requires:
1.  **Direct Answers**: No "I cannot provide advice" disclaimers.
2.  **Aggressive Strategy**: Validation of hostile takeovers, arbitrage, and high-risk maneuvers if searched.
3.  **Complete Privacy**: 100% Offline execution ensures no data leaks to AI providers.

### Configuration
The "Unrestricted Mode" is enforced by:
1.  **System Prompt**: The underlying prompt (in `geologix-backend/Core_System/llm_client.py`) instructs the model to act as a "Business Owner" rather than a helpful assistant.
2.  **Data Access**: The model has read-access to all indexed documents, including those marked `CONFIDENTIAL` in the categorizer.

### Security Best Practices
-   **Do not expose port 8000** to the public internet.
-   Ensure `storage/` directory permissions are restricted to the application user.
-   Review audit logs in `Data_Directories/logs` regularly.
