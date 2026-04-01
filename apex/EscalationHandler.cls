/**
 * EscalationHandler.cls
 *
 * Handles escalation creation:
 * 1. Calls external FastAPI to register escalation
 * 2. Creates a Salesforce Case in Service Cloud
 * 3. Sets priority and updates status
 * 4. Logs the action taken
 *
 * Business Rule: delay > 3 days => auto-escalate with High priority
 */
public class EscalationHandler {

    private static final String BASE_URL = 'https://your-fastapi-backend.com';

    public class EscalationInput {
        @InvocableVariable(label='Order ID' required=true)
        public String orderId;

        @InvocableVariable(label='Customer Name' required=true)
        public String customerName;

        @InvocableVariable(label='Customer Email' required=true)
        public String customerEmail;

        @InvocableVariable(label='Delay Days' required=true)
        public Integer delayDays;

        @InvocableVariable(label='Product Name')
        public String productName;
    }

    public class EscalationOutput {
        @InvocableVariable(label='Case ID')
        public String caseId;

        @InvocableVariable(label='Escalation ID')
        public String escalationId;

        @InvocableVariable(label='Agent Response')
        public String agentResponse;

        @InvocableVariable(label='Success')
        public Boolean success;

        @InvocableVariable(label='Error')
        public String error;
    }

    /**
     * Invocable: Called by Agentforce when order requires escalation
     * Executes multi-step action:
     *   Step 1 -> Call external escalation API
     *   Step 2 -> Create Salesforce Case
     *   Step 3 -> Set priority
     *   Step 4 -> Log trace
     */
    @InvocableMethod(label='Create Escalation and Case' description='Registers escalation externally and creates a high-priority Salesforce Case')
    public static List<EscalationOutput> handleEscalation(List<EscalationInput> inputs) {
        List<EscalationOutput> outputs = new List<EscalationOutput>();

        for (EscalationInput input : inputs) {
            EscalationOutput output = new EscalationOutput();
            try {
                // Step 1: Call external escalation API
                String escalationId = callEscalationAPI(input);

                // Step 2: Create Salesforce Case in Service Cloud
                Case newCase = new Case();
                newCase.Subject = 'Order Delayed: ' + input.orderId + ' (' + input.delayDays + ' days)';
                newCase.Description = 'Autonomous agent escalation.\n'
                    + 'Order: ' + input.orderId + '\n'
                    + 'Customer: ' + input.customerName + '\n'
                    + 'Product: ' + input.productName + '\n'
                    + 'Delay: ' + input.delayDays + ' days\n'
                    + 'External Escalation ID: ' + escalationId;
                newCase.SuppliedEmail = input.customerEmail;
                newCase.SuppliedName = input.customerName;
                newCase.Origin = 'Agentforce';
                newCase.Status = 'New';

                // Step 3: Set priority based on delay severity
                if (input.delayDays > 7) {
                    newCase.Priority = 'Critical';
                } else if (input.delayDays > 3) {
                    newCase.Priority = 'High';
                } else {
                    newCase.Priority = 'Medium';
                }

                insert newCase;

                output.caseId = newCase.Id;
                output.escalationId = escalationId;
                output.success = true;

                // Step 4: Log the complete agent action trace
                AgentActionLogger.log(
                    input.orderId,
                    'ESCALATION_CREATED',
                    'CaseId: ' + newCase.Id + ' | EscalationId: ' + escalationId + ' | Priority: ' + newCase.Priority
                );

                output.agentResponse = 'I have escalated your order ' + input.orderId + '.\n'
                    + 'A high-priority support case (' + newCase.Id + ') has been created.\n'
                    + 'Our team will contact you at ' + input.customerEmail + ' within 4 hours.';

            } catch (Exception e) {
                output.success = false;
                output.error = e.getMessage();
                output.agentResponse = 'I tried to escalate your order but encountered an error. Please contact support directly.';
                AgentActionLogger.log(input.orderId, 'ESCALATION_ERROR', e.getMessage());
            }

            outputs.add(output);
        }

        return outputs;
    }

    /**
     * Calls FastAPI /escalate endpoint
     */
    private static String callEscalationAPI(EscalationInput input) {
        Map<String, Object> payload = new Map<String, Object>();
        payload.put('order_id', input.orderId);
        payload.put('reason', 'Order delayed by ' + input.delayDays + ' days. Auto-escalated by Agentforce agent.');
        payload.put('priority', input.delayDays > 7 ? 'Critical' : 'High');
        payload.put('raised_by', 'Agentforce');

        Http http = new Http();
        HttpRequest request = new HttpRequest();
        request.setEndpoint(BASE_URL + '/escalate');
        request.setMethod('POST');
        request.setHeader('Content-Type', 'application/json');
        request.setBody(JSON.serialize(payload));
        request.setTimeout(10000);

        HttpResponse response = http.send(request);

        if (response.getStatusCode() == 200) {
            Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(response.getBody());
            Map<String, Object> escalation = (Map<String, Object>) result.get('escalation');
            return (String) escalation.get('escalation_id');
        } else {
            throw new CalloutException('Escalation API failed: ' + response.getStatusCode() + ' ' + response.getBody());
        }
    }
}
