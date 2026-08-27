import type { Task, TaskCreate, TaskUpdate } from '../types/task';
import type { TokenResponse, User } from '../types/auth';

const API_BASE_URL = 'http://127.0.0.1:8000';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export const api = {
  // --- AUTENTICACIÓN ---
  async register(email: string, password: string): Promise<User> {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error al registrar usuario');
    }
    return res.json();
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Credenciales inválidas');
    }
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Sesión expirada');
    return res.json();
  },

  // --- TAREAS MULTI-TENANT ---
  async getTasks(): Promise<Task[]> {
    const res = await fetch(`${API_BASE_URL}/tasks/`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Error al obtener tareas');
    return res.json();
  },

  async createTask(task: TaskCreate): Promise<Task> {
    const res = await fetch(`${API_BASE_URL}/tasks/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error('Error al crear tarea');
    return res.json();
  },

  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error('Error al actualizar tarea');
    return res.json();
  },

  async deleteTask(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Error al eliminar tarea');
  },
};