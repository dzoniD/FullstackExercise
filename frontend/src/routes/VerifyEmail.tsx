import { useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"


export default function SignIn() {
    const [params] = useSearchParams()
    const navigate = useNavigate()
    useEffect(() => {
        const token = params.get("token")
        if (!token) return
    
        fetch(`http://localhost:8001/auth/verify?token=${token}`)
          .then(res => res.json())
          .then((data) => {
            console.log(data)
            setTimeout(() => navigate("/login"), 2000)
          })
          .catch((error) => {
            console.error("Error verifying email:", error)
          })
      }, [])
   

  return (
     <p>Verifying your email...</p>
  );
}

