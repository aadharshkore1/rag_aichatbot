
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { FaUserCircle } from "react-icons/fa";
import { BsRobot } from "react-icons/bs";

function App() {

  // ---------------------------------
  // STATES
  // ---------------------------------

  const [message, setMessage] = useState("");

  const [chat, setChat] = useState([]);

  const [loading, setLoading] = useState(false);

  const [darkMode, setDarkMode] = useState(true);

  const [listening, setListening] = useState(false);

  const [uploadedPDF, setUploadedPDF] =
    useState("");

  const [uploadingPDF, setUploadingPDF] =
    useState(false);

  // ---------------------------------
  // AUTO SCROLL REF
  // ---------------------------------

  const chatEndRef = useRef(null);

  // ---------------------------------
  // AUTO SCROLL
  // ---------------------------------

  useEffect(() => {

    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });

  }, [chat, loading]);

  // ---------------------------------
  // SPEECH RECOGNITION
  // ---------------------------------

  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  const recognition =
    new SpeechRecognition();

  recognition.continuous = false;

  recognition.lang = "en-US";

  recognition.onstart = () => {

    setListening(true);

  };

  recognition.onend = () => {

    setListening(false);

  };

  recognition.onresult = (event) => {

    const transcript =
      event.results[0][0].transcript;

    setMessage(transcript);

  };

  // ---------------------------------
  // START LISTENING
  // ---------------------------------

  const startListening = () => {

    recognition.start();

  };

  // ---------------------------------
  // STOP SPEAKING
  // ---------------------------------

  const stopSpeaking = () => {

    window.speechSynthesis.cancel();

  };

  // ---------------------------------
  // TEXT TO SPEECH
  // ---------------------------------

  const speakText = (text) => {

    window.speechSynthesis.cancel();

    const speech =
      new SpeechSynthesisUtterance(text);

    speech.lang = "en-US";

    speech.rate = 1;

    speech.pitch = 1;

    window.speechSynthesis.speak(speech);

  };

  // ---------------------------------
  // PDF UPLOAD
  // ---------------------------------

  const uploadPDF = async (event) => {

    const file = event.target.files[0];

    if (!file) return;

    const formData = new FormData();

    formData.append("file", file);

    setUploadingPDF(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/upload-pdf",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (data.error) {

        alert(data.error);

      } else {

        setUploadedPDF(data.pdf_name);

        alert(
          "PDF Uploaded Successfully"
        );
      }

    } catch (error) {

      console.log(error);

      alert("PDF Upload Failed");

    } finally {

      setUploadingPDF(false);

    }
  };

  // ---------------------------------
  // SEND MESSAGE
  // ---------------------------------

  const sendMessage = async () => {

    if (!message) return;

    const userMessage = {

      role: "user",

      content: message
    };

    setChat((prev) => [

      ...prev,

      userMessage
    ]);

    const currentMessage = message;

    setMessage("");

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {

          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({

            message: currentMessage
          })
        }
      );

      const data = await response.json();

      const aiMessage = {

        role: "ai",

        content:
          data.response || data.error
      };

      setChat((prev) => [

        ...prev,

        aiMessage
      ]);

      speakText(aiMessage.content);

    } catch (error) {

      console.log(error);

    } finally {

      setLoading(false);

    }
  };

  // ---------------------------------
  // ENTER KEY
  // ---------------------------------

  const handleKeyPress = (e) => {

    if (e.key === "Enter") {

      sendMessage();

    }
  };

  return (

    <div style={{

      display: "flex",

      height: "100vh",

      backgroundColor:
        darkMode
          ? "#0f172a"
          : "#f1f5f9",

      color:
        darkMode
          ? "white"
          : "black",

      fontFamily: "Arial"
    }}>

      {/* SIDEBAR */}

      <div style={{

        width:
          window.innerWidth < 768
            ? "80px"
            : "260px",

        backgroundColor:
          darkMode
            ? "#111827"
            : "#e2e8f0",

        padding: "20px",

        display: "flex",

        flexDirection: "column"
      }}>

        <h2>

          {window.innerWidth < 768
            ? "AI"
            : "RAG Chatbot"}

        </h2>

        {/* DARK MODE */}

        <button

          onClick={() =>
            setDarkMode(!darkMode)
          }

          style={{

            padding: "10px",

            borderRadius: "10px",

            border: "none",

            cursor: "pointer",

            marginBottom: "20px"
          }}
        >

          {darkMode ? "☀️" : "🌙"}

        </button>

        {/* PDF STATUS */}

        <div style={{
          marginBottom: "20px"
        }}>

          <h4>Uploaded PDF</h4>

          <div style={{

            padding: "10px",

            borderRadius: "10px",

            backgroundColor:
              darkMode
                ? "#1e293b"
                : "white",

            fontSize: "14px"
          }}>

            {uploadingPDF
              ? "Uploading..."
              : uploadedPDF || "No PDF"}

          </div>

        </div>

        {/* RECENT CHATS */}

        {window.innerWidth > 768 && (

          <div>

            <h4>Recent Chats</h4>

            {chat.slice(-5).map(

              (msg, index) => (

              msg.role === "user" && (

                <div

                  key={index}

                  style={{

                    padding: "10px",

                    marginBottom: "10px",

                    borderRadius: "10px",

                    backgroundColor:
                      darkMode
                        ? "#1e293b"
                        : "white",

                    fontSize: "14px"
                  }}
                >

                  {msg.content.substring(0, 25)}...

                </div>
              )
            ))}

          </div>
        )}

      </div>

      {/* MAIN CHAT */}

      <div style={{

        flex: 1,

        display: "flex",

        flexDirection: "column"
      }}>

        {/* CHAT AREA */}

        <div style={{

          flex: 1,

          overflowY: "auto",

          padding: "20px"
        }}>

          {chat.map((msg, index) => (

            <div

              key={index}

              style={{

                display: "flex",

                justifyContent:
                  msg.role === "user"
                    ? "flex-end"
                    : "flex-start",

                marginBottom: "20px"
              }}
            >

              <div style={{

                display: "flex",

                alignItems: "flex-start",

                gap: "10px",

                maxWidth:
                  window.innerWidth < 768
                    ? "90%"
                    : "70%"
              }}>

                {/* AVATAR */}

                {msg.role === "ai" ? (

                  <BsRobot
                    size={30}
                    color="#38bdf8"
                  />

                ) : (

                  <FaUserCircle
                    size={30}
                    color="#22c55e"
                  />

                )}

                {/* CHAT BUBBLE */}

                <div style={{

                  padding: "15px",

                  borderRadius: "15px",

                  backgroundColor:
                    msg.role === "user"
                      ? "#2563eb"
                      : darkMode
                        ? "#1e293b"
                        : "#e2e8f0",

                  color:
                    msg.role === "user"
                      ? "white"
                      : darkMode
                        ? "white"
                        : "black"
                }}>

                  <ReactMarkdown>

                    {msg.content}

                  </ReactMarkdown>

                </div>

              </div>

            </div>
          ))}

          {/* LOADING */}

          {loading && (

            <div style={{

              display: "flex",

              alignItems: "center",

              gap: "10px"
            }}>

              <BsRobot
                size={30}
                color="#38bdf8"
              />

              <div style={{

                padding: "15px",

                borderRadius: "15px",

                backgroundColor:
                  darkMode
                    ? "#1e293b"
                    : "#e2e8f0"
              }}>

                AI is typing...

              </div>

            </div>
          )}

          <div ref={chatEndRef}></div>

        </div>

        {/* INPUT AREA */}

        <div style={{

          padding: "20px",

          display: "flex",

          gap: "10px",

          borderTop: "1px solid gray"
        }}>

          {/* INPUT */}

          <input

            type="text"

            value={message}

            onChange={(e) =>
              setMessage(e.target.value)
            }

            onKeyDown={handleKeyPress}

            placeholder="Ask something..."

            style={{

              flex: 1,

              padding: "15px",

              borderRadius: "10px",

              border: "none",

              outline: "none",

              fontSize: "16px"
            }}
          />

          {/* PDF BUTTON */}

          <label style={{

            padding: "15px",

            borderRadius: "10px",

            backgroundColor: "#9333ea",

            color: "white",

            cursor: "pointer"
          }}>

            +

            <input

              type="file"

              accept=".pdf"

              hidden

              onChange={uploadPDF}
            />

          </label>

          {/* MIC BUTTON */}

          <button

            onClick={startListening}

            style={{

              padding: "15px",

              borderRadius: "10px",

              border: "none",

              backgroundColor:
                listening
                  ? "#ef4444"
                  : "#22c55e",

              color: "white",

              cursor: "pointer"
            }}
          >

            {listening
              ? "Listening..."
              : "🎤"}

          </button>

          {/* SEND */}

          <button

            onClick={sendMessage}

            style={{

              padding: "15px 25px",

              borderRadius: "10px",

              border: "none",

              backgroundColor: "#2563eb",

              color: "white",

              cursor: "pointer"
            }}
          >

            Send

          </button>

          {/* STOP VOICE */}

          <button

            onClick={stopSpeaking}

            style={{

              padding: "15px 20px",

              borderRadius: "10px",

              border: "none",

              backgroundColor: "#ef4444",

              color: "white",

              cursor: "pointer"
            }}
          >

            Stop Voice

          </button>

        </div>

      </div>

    </div>
  );
}

export default App;

