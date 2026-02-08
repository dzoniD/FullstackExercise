
import Task from "../../components/Task";
import TaskFilters from "../../components/TagFilters";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useRef, useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { useQuery } from "@tanstack/react-query";

const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001';
const TASKS_API_URL = import.meta.env.VITE_TASKS_API_URL || 'http://localhost:8002';

export default function TasksPage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingTask, setEditingTask] = useState<any | null>(null);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    
    const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
    const [token, setToken] = useState<string | null>(null);
    // const { search } = useLocation();
    // const params = new URLSearchParams(search);
  
  
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    
  
  
    useEffect(() => {
      const storedToken = localStorage.getItem('token');
      setToken(storedToken);
  
      if (dialogOpen) {
        dialogRef.current?.showModal();
      } else {
        dialogRef.current?.close();
        // Resetuj forme i greške kada se dialog zatvori
        setTitle("");
        setDescription("");
        setErrors({});
        setEditingTask(null);
      }
    }, [dialogOpen]);
  
    const validateForm = (): boolean => {
      const newErrors: { title?: string; description?: string } = {};
  
      // Validacija title
      if (!title.trim()) {
        newErrors.title = "Naslov je obavezan";
      } else if (title.trim().length < 3) {
        newErrors.title = "Naslov mora imati najmanje 3 karaktera";
      } else if (title.trim().length > 100) {
        newErrors.title = "Naslov ne može biti duži od 100 karaktera";
      }
  
      // Validacija description
      if (!description.trim()) {
        newErrors.description = "Opis je obavezan";
      } else if (description.trim().length < 5) {
        newErrors.description = "Opis mora imati najmanje 5 karaktera";
      } else if (description.trim().length > 500) {
        newErrors.description = "Opis ne može biti duži od 500 karaktera";
      }
  
      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    };
  
    const { data: count = [], isLoading, isError } = useQuery({
      queryKey: ["tasks", { selectedTags }],//tagsParam, mode
      queryFn: async () => {
        let params = selectedTags.length ? `?tags=${selectedTags.map(tag => tag.name).join(",")}&mode=${mode}` : "";
  
        const response = await fetch(`${TASKS_API_URL}/tasks${params}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });


        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error("Error response:", errorData);
            throw new Error(errorData.detail?.[0]?.msg || "Greška pri kreiranju tiketa");
          }

        return response.json();
      },
      enabled: !!token,
    });
  
    const createTaskMutation = useMutation({
      mutationFn: async (newTask: { title: string; description: string }) => {
        const response = await fetch(`${TASKS_API_URL}/tasks`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(newTask),
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error("Error response:", errorData);
          throw new Error(errorData.detail?.[0]?.msg || "Greška pri kreiranju tiketa");
        }
        return response.json();
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
        setDialogOpen(false);
        setTitle("");
        setDescription("");
        setErrors({});
        setEditingTask(null);
      },
      onError: (error: Error) => {
        // Prikaži grešku ako dođe do problema sa serverom
        setErrors({ description: error.message });
      },
    });
  
    const updateTaskMutation = useMutation({
      mutationFn: async ({ id, task }: { id: number; task: { title: string; description: string } }) => {
        const response = await fetch(`${TASKS_API_URL}/tasks/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(task),
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error("Error response:", errorData);
          throw new Error(errorData.detail?.[0]?.msg || "Greška pri ažuriranju tiketa");
        }
        return response.json();
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
        setDialogOpen(false);
        setTitle("");
        setDescription("");
        setErrors({});
        setEditingTask(null);
      },
      onError: (error: Error) => {
        // Prikaži grešku ako dođe do problema sa serverom
        setErrors({ description: error.message });
      },
    });
  
    const handleEditTask = (task: any) => {
      setEditingTask(task);
      setTitle(task.title);
      setDescription(task.description);
      setErrors({});
      setDialogOpen(true);
    };
  
  
  
    if (isLoading) {
      return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-xl text-gray-600 dark:text-gray-400">Učitavanje...</div>
        </div>
      );
    }
  
    if (isError) {
      return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-xl text-red-600">Greška pri učitavanju tiketa</div>
        </div>
      );
    }
  
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-8 text-center">
            Tiketi
          </h1>
          <TaskFilters selectedTags={selectedTags} setSelectedTags={setSelectedTags} />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {count.map((task: any) => (
             <Task key={task.id} task={task} onEdit={handleEditTask} />
            ))}
          </div>
          <button 
            onClick={() => {
              setEditingTask(null);
              setTitle("");
              setDescription("");
              setErrors({});
              setDialogOpen(true);
            }}
            className="bg-blue-500 mt-4 px-4 py-2 rounded-md hover:bg-blue-600 transition-colors text-white font-medium"
          >
            Dodaj novi tiket
          </button>
        </div>
  
        <dialog 
          ref={dialogRef}
          className="w-full max-w-md rounded-lg shadow-xl p-6 bg-white dark:bg-gray-800 backdrop:bg-black/50"
        >
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
              {editingTask ? "Izmeni tiket" : "Novi tiket"}
            </h2>
            
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Naslov <span className="text-red-500">*</span>
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  // Ukloni grešku kada korisnik počne da kuca
                  if (errors.title) {
                    setErrors({ ...errors, title: undefined });
                  }
                }}
                className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white ${
                  errors.title
                    ? "border-red-500 focus:ring-red-500"
                    : "border-gray-300 dark:border-gray-600"
                }`}
                placeholder="Unesite naslov..."
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title}</p>
              )}
            </div>
  
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Opis <span className="text-red-500">*</span>
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  // Ukloni grešku kada korisnik počne da kuca
                  if (errors.description) {
                    setErrors({ ...errors, description: undefined });
                  }
                }}
                rows={4}
                className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white ${
                  errors.description
                    ? "border-red-500 focus:ring-red-500"
                    : "border-gray-300 dark:border-gray-600"
                }`}
                placeholder="Unesite opis..."
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description}</p>
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {description.length}/500 karaktera
              </p>
            </div>
  
            <div className="flex gap-3 justify-end mt-6">
              <button
                onClick={() => {
                  setDialogOpen(false);
                }}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
              >
                Otkaži
              </button>
              <button
                onClick={() => {
                  if (validateForm()) {
                    if (editingTask) {
                      updateTaskMutation.mutate({
                        id: editingTask.id,
                        task: {
                          title: title.trim(),
                          description: description.trim()
                        }
                      });
                    } else {
                      createTaskMutation.mutate({ 
                        title: title.trim(), 
                        description: description.trim() 
                      });
                    }
                  }
                }}
                disabled={createTaskMutation.isPending || updateTaskMutation.isPending}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {(createTaskMutation.isPending || updateTaskMutation.isPending) 
                  ? "Čuvanje..." 
                  : editingTask 
                    ? "Sačuvaj izmene" 
                    : "Sačuvaj"}
              </button>
            </div>
          </div>
        </dialog>
      </div>
    );
  }