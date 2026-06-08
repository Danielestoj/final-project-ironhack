import client from "./client";

export async function login(email, password) {
  const res = await client.post("/auth/login", { email, password });
  localStorage.setItem("token", res.data.access_token);
  localStorage.setItem("user", JSON.stringify(res.data.usuario));
  return res.data;
}

export async function register(email, password, nombre) {
  const res = await client.post("/auth/registro", { email, password, nombre });
  localStorage.setItem("token", res.data.access_token);
  localStorage.setItem("user", JSON.stringify(res.data.usuario));
  return res.data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function getToken() {
  return localStorage.getItem("token");
}

export function getUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}
