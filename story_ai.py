"""LangGraph bổ sung ngữ cảnh của cảnh truyện trước khi gọi DeepSeek."""
from langgraph.graph import END, START, StateGraph
from ai import ask_deepseek, AdviceState
from career_stories import get_story


class StoryState(AdviceState,total=False):
    career_id: str
    scene_index: int
    question: str
    context: str
    answer: str


def story_context(state):
    story = get_story(state["career_id"])
    panel = story["scenes"][state["scene_index"]]
    return {"context": (
        f"Học sinh đang xem truyện minh họa nghề {story['name']}. "
        f"Cảnh đang xem: {panel['title']}. Nội dung: {panel['caption']}. "
        f"Kỹ năng: {panel['skill']}. Tổng kết nghề: {story['takeaway']}. "
        "Giải thích câu hỏi dựa vào cảnh này. Đây là mô phỏng khám phá nghề; "
        "không đưa hướng dẫn điều trị, kê thuốc hoặc thao tác nghề nguy hiểm. "
        "Không suy luận tính cách hay độ phù hợp của học sinh từ lựa chọn câu hỏi tương tác."
    )}


builder = StateGraph(StoryState)
builder.add_node("story_context", story_context)
builder.add_node("deepseek", ask_deepseek)
builder.add_edge(START, "story_context")
builder.add_edge("story_context", "deepseek")
builder.add_edge("deepseek", END)
story_graph = builder.compile()
