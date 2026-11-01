async function send() {
  const message = document.getElementById("message").value;
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const { reply } = await res.json();
  const bubble = document.createElement("div");
  bubble.className = "bubble assistant";
  bubble.innerHTML = reply;
  document.getElementById("log").appendChild(bubble);
}
