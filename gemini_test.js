import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI("AIzaSyBaRfhQEXo9ONJNMX_VXTE6GXYJYUDLRFk");
const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

const result = await model.generateContent("Say hello from Gemini!");
console.log(result.response.text());
