/**
 * AgentResponseBuilder.cls
 *
 * Builds natural language responses for the Agentforce agent.
 * Centralizes all response templates so the agent always
 * communicates clearly and consistently.
 */
public class AgentResponseBuilder {

    /**
     * Builds the order status response message
     * based on order state and delay analysis.
     */
    public static String buildOrderResponse(
        String status,
        Integer delayDays,
        String customerName,
        Boolean requiresEscalation
    ) {
        String greeting = 'Hi ' + customerName + ', ';

        if (status == 'delivered') {
            return greeting + 'your order has been successfully delivered. Is there anything else I can help you with?';
        }

        if (status == 'in_transit') {
            return greeting + 'your order is currently in transit and on schedule. You should receive it within the expected delivery window.';
        }

        if (status == 'delayed') {
            String delayMsg = greeting + 'your order is currently delayed by ' + delayDays + ' day(s). ';
            if (requiresEscalation) {
                delayMsg += 'Because the delay exceeds our 3-day threshold, I am automatically escalating this to our support team. ';
                delayMsg += 'You will be contacted within 4 hours with a resolution update.';
            } else {
                delayMsg += 'Our team is actively working to resolve this. We appreciate your patience.';
            }
            return delayMsg;
        }

        return greeting + 'your order status is: ' + status + '. Please contact support if you need further assistance.';
    }

    /**
     * Builds a confirmation message after escalation action is taken.
     */
    public static String buildEscalationConfirmation(String orderId, String caseId, String customerEmail) {
        return 'I have successfully escalated order ' + orderId + '.\n'
            + 'A high-priority support case (ID: ' + caseId + ') has been created in our system.\n'
            + 'Our support team will contact you at ' + customerEmail + ' within 4 hours.\n'
            + 'Thank you for your patience.';
    }

    /**
     * Builds a friendly error message for the agent to return.
     */
    public static String buildErrorResponse(String context) {
        return 'I encountered an issue while processing your request (' + context + '). '
            + 'Please try again or contact our support team directly for immediate assistance.';
    }
}
