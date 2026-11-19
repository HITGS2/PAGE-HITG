
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.6.0/firebase-app.js";

import {
  getFirestore,
  collection,
  getDocs
} from "https://www.gstatic.com/firebasejs/12.6.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCfFDbcl3zUel1fnM8CbcknGeT5KAhpf18",
  authDomain: "page-hitg-b83e1.firebaseapp.com",
  projectId: "page-hitg-b83e1",
  storageBucket: "page-hitg-b83e1.firebasestorage.app",
  messagingSenderId: "218687624946",
  appId: "1:218687624946:web:70bee81bcdf7ea8060626b",
  measurementId: "G-K07R5CBJ29"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function loadPublicSchedules() {
  try {
    const snapshot = await getDocs(collection(db, "schedules"));

    const firebaseSchedules = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));

    // 기존 수동 일정 대신 Firebase 일정 사용
    schedules.splice(
      0,
      schedules.length,
      ...firebaseSchedules
    );

    // 현재 스케줄 화면이 열려 있다면 새로 표시
    const schedulePage = document.getElementById("schedulePage");

    if (schedulePage?.classList.contains("active")) {
      renderSchedules();
    }

    console.log("Firebase 일정 불러오기 성공:", firebaseSchedules.length);

  } catch (error) {
    console.error("Firebase 일정 불러오기 실패:", error);
  }
}

loadPublicSchedules();
