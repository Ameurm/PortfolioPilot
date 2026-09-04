from rag_service import answer_question


question = "How did you implement RAG?"

answer = answer_question(question)


print()
print("=" * 70)
print("QUESTION")
print("=" * 70)
print(question)

print()
print("=" * 70)
print("RAG ANSWER")
print("=" * 70)
print(answer)