/**
 * AgentActionLogger.cls
 *
 * Provides agent decision tracing and audit logging.
 * Creates Agent_Log__c custom object records to track:
 * - What action the agent took
 * - What data it received
 * - What decision it made
 * - Timestamp of each step
 *
 * This enables full observability of autonomous agent decisions.
 * (Optional but powerful for demo: shows you understand agentic observability)
 */
public class AgentActionLogger {

    /**
     * Logs an agent action to the Agent_Log__c custom object.
     * 
     * NOTE: You must create the Agent_Log__c custom object in your
     * Salesforce Dev org with the following fields:
     *   - Order_Id__c (Text)
     *   - Action_Type__c (Text)
     *   - Details__c (Long Text Area)
     *   - Timestamp__c (DateTime)
     *
     * @param orderId    The order being processed
     * @param actionType The action taken (ORDER_FETCH, ESCALATION_CREATED, ERROR, etc.)
     * @param details    Details about the decision or data received
     */
    public static void log(String orderId, String actionType, String details) {
        try {
            // Using a generic SObject insert to avoid compile errors
            // if the custom object hasn't been created yet in the org.
            // Replace with strongly-typed class once Agent_Log__c is deployed.
            SObject logRecord = (SObject) Type.forName('Agent_Log__c').newInstance();
            logRecord.put('Order_Id__c', orderId);
            logRecord.put('Action_Type__c', actionType);
            logRecord.put('Details__c', details);
            logRecord.put('Timestamp__c', Datetime.now());
            insert logRecord;
        } catch (Exception e) {
            // Fail silently - logging should never break the main agent flow
            System.debug('AgentActionLogger failed: ' + e.getMessage());
        }
    }

    /**
     * Retrieves recent logs for a given order.
     * Used for debugging and demo visualization.
     */
    public static List<SObject> getLogsForOrder(String orderId) {
        try {
            return Database.query(
                'SELECT Order_Id__c, Action_Type__c, Details__c, Timestamp__c '
                + 'FROM Agent_Log__c '
                + 'WHERE Order_Id__c = :orderId '
                + 'ORDER BY Timestamp__c DESC '
                + 'LIMIT 20'
            );
        } catch (Exception e) {
            System.debug('AgentActionLogger query failed: ' + e.getMessage());
            return new List<SObject>();
        }
    }
}
