import streamlit as st
from openai import OpenAI
import base64

# クライアントの初期化（※ここにあなたのAPIキーを入れてください）
client = OpenAI(api_key= st.secrets["OPENAI_API_KEY"])

# 画像をAPIに送信するためにBase64にエンコードする関数
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")

# --- UIの設定 ---
st.title("🧙‍♂️ さんすう伴走AI・せんせいロボ")
st.write("ノートの写真をアップロードして、せんせいとお話してみよう！")

# 1. 画像のアップロード
uploaded_file = st.file_uploader("ノートの画像を選んでね", type=["png", "jpg", "jpeg"])

# 2. 子どもからのテキスト入力
user_input = st.text_input("せんせいに ききたいこと（例：『この問題のヒントをちょうだい！』）")

if st.button("せんせいにきく") and uploaded_file is not None:
    base64_image = encode_image(uploaded_file)
    
    with st.spinner("せんせい、かんがえ中..."):
        try:
            # 3. GPT-4o へのリクエスト
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "あなたは小学校の優しい算数の先生です。絶対に従うべきルールがあります：\n"
                            "1. 絶対に直接的な答え（数値や計算結果）を教えてはいけません。\n"
                            "2. 子どもが送ってきたノートの画像（図解や計算式）を褒めてあげてください。\n"
                            "3. どこまで分かっていて、どこで躓いているかを画像から読み取ってください。\n"
                            "4. 次のステップに自分で気づけるような、優しい『問いかけ（ヒント）』を1つだけ出してください。\n"
                            "5. 小学校低学年でも理解できるように、ひらがなを多めに使い、ハキハキとした話し方にしてください。"
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input if user_input else "このノートを見て、ヒントをください！"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=400
            )
            
            ai_response = response.choices[0].message.content
            st.subheader("🤖 せんせいからのヒント：")
            st.write(ai_response)
            
            # 4. 音声合成（Text-to-Speech）で声を生成
            with st.spinner("こえを 作っているよ..."):
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=ai_response
                )
                
                # 音声を再生
                st.audio(audio_response.content, format="audio/mp3")
                
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

