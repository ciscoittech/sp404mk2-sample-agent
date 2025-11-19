
import firebase from "firebase/compat/app";
import "firebase/compat/auth";
import "firebase/compat/database";

const firebaseConfig = {
  apiKey: "AIzaSyCygO5qSwM1bHwUAj_KnD4rvHADcbIzApM",
  authDomain: "nextjsproject-d396c.firebaseapp.com",
  projectId: "nextjsproject-d396c",
  storageBucket: "nextjsproject-d396c.firebasestorage.app",
  messagingSenderId: "90305865005",
  appId: "1:90305865005:web:b667ca440608b3be159fa4",
  databaseURL: "https://nextjsproject-d396c-default-rtdb.firebaseio.com/",
};

if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

const Db = firebase.database();
const Auth = firebase.auth();

export { Db, Auth, firebase };
