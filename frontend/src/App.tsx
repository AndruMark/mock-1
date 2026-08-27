import React, { useEffect, useState } from 'react';
import { api } from './services/api';
import type { Task } from './types/task';
import {
  CheckCircle2,
  Circle,
  Trash2,
  Plus,
  RefreshCw,
  BarChart2,
  AlertTriangle,
  X,
  Check,
  Filter,
} from 'lucide-react';
import './App.css';

type FilterType = 'all' | 'pending' | 'completed';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<FilterType>('all');
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  const removeToast = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const data = await api.getTasks();
      setTasks(data);
    } catch {
      addToast('No se pudo conectar con el backend (FastAPI en :8000).', 'error');
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
      addToast(`Tarea "${newTask.title}" creada correctamente.`);
    } catch {
      addToast('Error al persistir la tarea.', 'error');
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const updated = await api.updateTask(task.id, { completed: !task.completed });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
      addToast(
        updated.completed
          ? `Tarea "${task.title}" marcada como completada.`
          : `Tarea "${task.title}" reactivada.`
      );
    } catch {
      addToast('Error al actualizar el estado.', 'error');
    }
  };

  const confirmDelete = async () => {
    if (!taskToDelete) return;
    try {
      await api.deleteTask(taskToDelete.id);
      setTasks((prev) => prev.filter((t) => t.id !== taskToDelete.id));
      addToast(`Tarea "${taskToDelete.title}" eliminada con éxito.`, 'info');
    } catch {
      addToast('Error al eliminar la tarea.', 'error');
    } finally {
      setTaskToDelete(null);
    }
  };

  // Métricas
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Filtrado reactivo
  const filteredTasks = tasks.filter((task) => {
    if (filter === 'pending') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  return (
    <div className="container">
      {/* Toast Notification Container */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {t.type === 'success' && <Check size={18} />}
            {t.type === 'error' && <AlertTriangle size={18} />}
            {t.type === 'info' && <BarChart2 size={18} />}
            <span>{t.message}</span>
            <button className="toast-close" onClick={() => removeToast(t.id)}>
              <X size={14} />
            </button>
          </div>
        ))}
      </div>

      {/* Modal de Confirmación de Borrado */}
      {taskToDelete && (
        <div className="modal-overlay" onClick={() => setTaskToDelete(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <AlertTriangle className="text-warning" size={24} />
              <h3>¿Eliminar tarea?</h3>
            </div>
            <p className="modal-body">
              Estás a punto de borrar permanentemente la tarea{' '}
              <strong>"{taskToDelete.title}"</strong>. Esta acción no se puede deshacer.
            </p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setTaskToDelete(null)}>
                Cancelar
              </button>
              <button className="btn-danger" onClick={confirmDelete}>
                Eliminar definitivamente
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="header">
        <div className="title-section">
          <h1>Mock-1 Dashboard</h1>
          <p className="subtitle">FastAPI Microservice + React / TypeScript Client</p>
        </div>
        <button className="btn-refresh" onClick={fetchTasks} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Actualizar
        </button>
      </header>

      {/* Grid de Métricas */}
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

      {/* Formulario de Alta */}
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

      {/* Barra de Filtros */}
      <div className="filter-bar">
        <div className="filter-label">
          <Filter size={16} />
          <span>Filtrar por:</span>
        </div>
        <div className="filter-tabs">
          <button
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            Todas ({totalTasks})
          </button>
          <button
            className={`filter-tab ${filter === 'pending' ? 'active' : ''}`}
            onClick={() => setFilter('pending')}
          >
            Pendientes ({pendingTasks})
          </button>
          <button
            className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completadas ({completedTasks})
          </button>
        </div>
      </div>

      {/* Listado de Tareas */}
      <main className="tasks-container">
        {loading && tasks.length === 0 ? (
          <p className="empty-state">Cargando tareas...</p>
        ) : filteredTasks.length === 0 ? (
          <div className="empty-state">
            <BarChart2 size={48} opacity={0.3} />
            <p>
              {filter === 'all'
                ? 'No hay tareas registradas. ¡Creá la primera arriba!'
                : filter === 'pending'
                ? '¡Genial! No tenés tareas pendientes.'
                : 'Aún no has completado ninguna tarea.'}
            </p>
          </div>
        ) : (
          <ul className="task-list">
            {filteredTasks.map((task) => (
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
                  onClick={() => setTaskToDelete(task)}
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