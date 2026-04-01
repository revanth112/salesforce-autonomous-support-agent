/**
 * OrderServiceCallout.cls
 * 
 * Makes HTTP callout to external Python FastAPI backend
 * to fetch real-time order details.
 * 
 * Called by: Agentforce Action (Invocable Method)
 * Endpoint: POST /orders/{orderId}
 */
public class OrderServiceCallout {

    private static final String BASE_URL = 'https://your-fastapi-backend.com'; // Replace with ngrok/deployed URL
    private static final Integer DELAY_THRESHOLD_DAYS = 3;

    /**
     * Wrapper class for Agentforce invocable input
     */
    public class OrderRequest {
        @InvocableVariable(label='Order ID' required=true)
        public String orderId;
    }

    /**
     * Wrapper class for Agentforce invocable output
     */
    public class OrderResult {
        @InvocableVariable(label='Order Status')
        public String status;

        @InvocableVariable(label='Delay Days')
        public Integer delayDays;

        @InvocableVariable(label='Customer Name')
        public String customerName;

        @InvocableVariable(label='Customer Email')
        public String customerEmail;

        @InvocableVariable(label='Product Name')
        public String productName;

        @InvocableVariable(label='Expected Delivery')
        public String expectedDelivery;

        @InvocableVariable(label='Tracking Number')
        public String trackingNumber;

        @InvocableVariable(label='Requires Escalation')
        public Boolean requiresEscalation;

        @InvocableVariable(label='Agent Response')
        public String agentResponse;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    /**
     * Main invocable method called by Agentforce
     * Understands intent -> Fetches order -> Decides if escalation needed
     */
    @InvocableMethod(label='Get Order Status and Decide Action' description='Fetches order from external system and determines if escalation is needed')
    public static List<OrderResult> getOrderAndDecide(List<OrderRequest> requests) {
        List<OrderResult> results = new List<OrderResult>();

        for (OrderRequest req : requests) {
            OrderResult result = new OrderResult();
            try {
                // Step 1: Call external API
                HttpResponse response = callExternalOrderAPI(req.orderId);

                if (response.getStatusCode() == 200) {
                    // Step 2: Parse the response
                    Map<String, Object> orderData = (Map<String, Object>) JSON.deserializeUntyped(response.getBody());

                    result.status = (String) orderData.get('status');
                    result.delayDays = (Integer) orderData.get('delay_days');
                    result.customerName = (String) orderData.get('customer_name');
                    result.customerEmail = (String) orderData.get('customer_email');
                    result.productName = (String) orderData.get('product');
                    result.expectedDelivery = (String) orderData.get('expected_delivery');
                    result.trackingNumber = (String) orderData.get('tracking_number');

                    // Step 3: Business logic decision
                    result.requiresEscalation = (result.delayDays != null && result.delayDays > DELAY_THRESHOLD_DAYS);

                    // Step 4: Log the agent trace
                    AgentActionLogger.log(
                        req.orderId,
                        'ORDER_FETCH',
                        'Status: ' + result.status + ' | Delay: ' + result.delayDays + ' days | Escalate: ' + result.requiresEscalation
                    );

                    // Step 5: Build agent response
                    result.agentResponse = AgentResponseBuilder.buildOrderResponse(result.status, result.delayDays, result.customerName, result.requiresEscalation);

                } else if (response.getStatusCode() == 404) {
                    result.errorMessage = 'Order ' + req.orderId + ' not found in the system.';
                    result.agentResponse = 'I could not find order ' + req.orderId + '. Please verify the order ID and try again.';
                } else {
                    result.errorMessage = 'External system returned error: ' + response.getStatusCode();
                    result.agentResponse = 'I encountered an issue while fetching your order. Please try again in a moment.';
                }

            } catch (Exception e) {
                result.errorMessage = 'Callout failed: ' + e.getMessage();
                result.agentResponse = 'I am unable to connect to the order management system right now. Please contact support.';
                AgentActionLogger.log(req.orderId, 'ERROR', e.getMessage());
            }

            results.add(result);
        }

        return results;
    }

    /**
     * Private helper: Makes HTTP GET request to FastAPI backend
     */
    private static HttpResponse callExternalOrderAPI(String orderId) {
        Http http = new Http();
        HttpRequest request = new HttpRequest();
        request.setEndpoint(BASE_URL + '/orders/' + orderId);
        request.setMethod('GET');
        request.setHeader('Content-Type', 'application/json');
        request.setHeader('Accept', 'application/json');
        request.setTimeout(10000); // 10 seconds timeout
        return http.send(request);
    }
}
