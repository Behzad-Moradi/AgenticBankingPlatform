import base64

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

from backend.schemas.account_opening import DriverLicenceDetails


vision_llm = init_chat_model("gpt-4.1-mini")

driver_licence_extractor = vision_llm.with_structured_output(
    DriverLicenceDetails
)


def extract_driver_licence(
    content: bytes,
    content_type: str,
) -> DriverLicenceDetails:

    encoded = base64.b64encode(content).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Extract the following information from this driver "
                    "licence: full name, date of birth, residential address, "
                    "and licence number. "
                    "Do not guess missing or unreadable information. "
                    "Return null for any field that cannot be reliably read."
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{content_type};base64,{encoded}",
                },
            },
        ]
    )

    return driver_licence_extractor.invoke([message])