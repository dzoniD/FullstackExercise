import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";

const TASKS_API_URL = import.meta.env.VITE_TASKS_API_URL || 'http://localhost:8002';


export default function TaskFilters({ selectedTags, setSelectedTags }) {
    const [token, setToken] = useState<string | null>(null);


    const { data: tags = [], isLoading, isError } = useQuery({
        queryKey: ["tags"],
        queryFn: async () => {
    
          const response = await fetch(`${TASKS_API_URL}/tags`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          return response.json();
        },
        enabled: !!token,
      });
  

      useEffect(() => {
        const storedToken = localStorage.getItem('token');
        setToken(storedToken);
        
      }, []);
    // checked={selectedTags.includes(tag)}
    // onChange={e => {
    //   if (e.target.checked) {
    //     setSelectedTags([...selectedTags, tag]);
    //   } else {
    //     setSelectedTags(selectedTags.filter(t => t !== tag));
    //   }
    // }}

    return (
      <div>
        {tags.map(tag => (
          <label key={tag.id}>
            <input
              type="checkbox"
              value={tag.name}
              checked={selectedTags.includes(tag)}
            onChange={e => {
            if (e.target.checked) {
                setSelectedTags([...selectedTags, tag]);
            } else {
                setSelectedTags(selectedTags.filter(t => t !== tag));
            }
            }}
        />
            {tag.name}
          </label>
        ))}
      </div>
    );
  }