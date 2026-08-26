import React, { useEffect, useState } from 'react';
import { api } from './services/api';
import type { Task } from './types/task';
import { CheckCircle2, Circle, Trash2, Plus, RefreshCw, BarChart2 } from 'lucide-react';
import './App.css';

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getTasks();
      setTasks(data);
    } catch (err) {
      setError('No se pudo conectar con el servidor backend (FastAPI en :8000).');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      const newTask = await api.createTask({
        title: title.trim(),
        description: description.trim() || undefined,
        completed: false,
      });
      setTasks((prev) => [...prev, newTask]);
      setTitle('');
      setDescription('');
    } catch (err) {
      alert('Error al crear la tarea');
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const updated = await api.updateTask(task.id, { completed: !task.completed });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err) {
      alert('Error al actualizar la tarea');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      alert('Error al eliminar la tarea');
    }
  };

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="container">
      <header className="header">
        <div className="title-section">
          <h1>Mock-1 Dashboard</h1>
          <p className="subtitle">FastAPI Backend + React / TypeScript Client</p>
        </div>
        <button className="btn-refresh" onClick={fetchTasks} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Actualizar
        </button>
      </header>

      <section className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Total Tareas</span>
          <span className="metric-value">{totalTasks}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Completadas</span>
          <span className="metric-value text-success">{completedTasks}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Pendientes</span>
          <span className="metric-value text-warning">{pendingTasks}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Tasa de Éxito</span>
          <span className="metric-value">{completionRate}%</span>
        </div>
      </section>

      {error && <div className="error-banner">{error}</div>}

      <form className="task-form" onSubmit={handleCreateTask}>
        <div className="input-group">
          <input
            type="text"
            placeholder="Título de la tarea (mín. 3 caracteres)..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            minLength={3}
          />
          <input
            type="text"
            placeholder="Descripción opcional..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary">
          <Plus size={18} />
          Nueva Tarea
        </button>
      </form>

      <main className="tasks-container">
        {loading && tasks.length === 0 ? (
          <p className="empty-state">Cargando tareas...</p>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <BarChart2 size={48} opacity={0.3} />
            <p>No hay tareas registradas. ¡Creá la primera arriba!</p>
          </div>
        ) : (
          <ul className="task-list">
            {tasks.map((task) => (
              <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
                <button
                  className="btn-icon check-btn"
                  onClick={() => handleToggleComplete(task)}
                >
                  {task.completed ? (
                    <CheckCircle2 className="text-success" size={22} />
                  ) : (
                    <Circle size={22} />
                  )}
                </button>
                <div className="task-info">
                  <h3>{task.title}</h3>
                  {task.description && <p>{task.description}</p>}
                  <span className="timestamp">
                    ID #{task.id} • {new Date(task.created_at).toLocaleDateString()}
                  </span>
                </div>
                <button
                  className="btn-icon delete-btn"
                  onClick={() => handleDelete(task.id)}
                  title="Eliminar tarea"
                >
                  <Trash2 size={18} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}