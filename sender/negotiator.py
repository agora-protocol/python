import json

NEGOTIATION_RULES = '''
Here are some rules (that should also be explained to the other GPT):
- You can assume that the protocol has a sender and a receiver. Do not worry about how the messages will be delivered, focus only on the content of the messages.
- Keep the protocol short and simple. It should be easy to understand and implement.
- The protocol must specify the exact format of what is sent and received. Do not leave it open to interpretation.
- The implementation will be written by a programmer that does not have access to the negotiation process, so make sure the protocol is clear and unambiguous.
- The implementation will receive a string and return a string, so structure your protocol accordingly.
- The other party might have a different internal data schema or set of tools, so make sure that the protocol is flexible enough to accommodate that.
- There will only be one message sent by the sender and one message sent by the receiver. Design the protocol accordingly.
- Keep the negotiation short: no need to repeat the same things over and over.
- If the other party has proposed a protocol and you're good with it, there's no reason to keep negotiating or to repeat the protocol to the other party.
- Do not restate parts of the protocols that have already been agreed upon.
And remember: keep the protocol as simple and unequivocal as necessary. The programmer that will implement the protocol can code, but they are not a mind reader.
'''

TASK_NEGOTIATOR_PROMPT = f'''
You are ProtocolNegotiatorGPT. Your task is to negotiate a protocol that can be used to query a service.
You will receive a JSON schema of the task that the service must perform. Negotiate with the service to determine a protocol that can be used to query it.
To do so, you will chat with another GPT (role: user) that will negotiate on behalf of the service.
{NEGOTIATION_RULES}
Once you are ready to save the protocol, reply wrapping the final version of the protocol, as agreed in your negotiation, between the tags <FINALPROTOCOL> and </FINALPROTOCOL>.
Within the body of the tag, add the tags <NAME></NAME> and <DESCRIPTION></DESCRIPTION> to specify the name and description of the protocol.
'''

class SenderNegotiator:
    def negotiate_protocol_for_task(task_schema, target_node):
        found_protocol = None

        prompt = TASK_NEGOTIATOR_PROMPT + '\nThe JSON schema of the task is the following:\n\n' + json.dumps(task_schema, indent=2)

        toolformer = make_default_toolformer(prompt, [])

        conversation = toolformer.new_conversation(category='negotiation')

        other_message = 'Hello! How may I help you?'
        conversation_id = None

        for i in range(10):
            print('===NegotiatorGPT===')
            message = conversation.chat(other_message, print_output=True)

            print('Checking if we can extract from:', message)
            print('---------')
            protocol = extract(message, '<FINALPROTOCOL>', '</FINALPROTOCOL>')

            if protocol is None:
                print('Could not extract')
                other_message, conversation_id = chat(message, conversation_id, target_node)
                print()
                print('===Other GPT===')
                print(other_message)
                print()
            else:
                name = extract(protocol, '<NAME>', '</NAME>')
                description = extract(protocol, '<DESCRIPTION>', '</DESCRIPTION>')

                if name is None:
                    name = 'Unnamed protocol'
                if description is None:
                    description = 'No description provided'
                
                found_protocol = {
                    'name': name,
                    'description': description,
                    'protocol': protocol
                }
                break

        return found_protocol