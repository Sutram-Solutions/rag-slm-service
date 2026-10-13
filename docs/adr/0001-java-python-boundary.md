# ADR 0001: Java/Python responsibility boundary

Python owns ingestion and retrieval evidence. Java owns authorization,
business facts, prompts, generation, conversation, and answer validation.
Clients call Java, which supplies a trusted explicit authorization scope to
Python. Python never calls a generation model.
