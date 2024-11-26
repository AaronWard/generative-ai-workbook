# from spin_sdk.http import IncomingHandler, Request, Response

# class IncomingHandler(IncomingHandler):
#     def handle_request(self, request: Request) -> Response:
#         return Response(
#             200,
#             {"content-type": "text/plain"},
#             bytes("Hello from Python!", "utf-8")
#         )



import chainlit as cl


@cl.on_chat_start
async def main():
    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="continue", value="continue", label="✅ Continue"),
            cl.Action(name="cancel", value="cancel", label="❌ Cancel"),
        ],
    ).send()

    if res and res.get("value") == "continue":
        await cl.Message(
            content="Continue!",
        ).send()