import type { Task, TaskCreate, TaskUpdate } from '../types/task';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  async getTasks(): Promise<Task[]> {
    const res = await fetch(`${API_BASE_URL}/tasks/`);
    if (!res.ok) throw new Error('Error al obtener tareas');
    return res.json();
  },

  async createTask(task: TaskCreate): Promise<Task> {
    const res = await fetch(`${API_BASE_URL}/tasks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error('Error al crear tarea');
    return res.json();
  },

  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error('Error al actualizar tarea');
    return res.json();
  },

  async deleteTask(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Error al eliminar tarea');
  },
};