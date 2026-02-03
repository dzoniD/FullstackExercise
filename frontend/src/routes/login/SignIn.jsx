import { useForm } from "react-hook-form";

export default function SignIn() {
const {register, handleSubmit, formState: {errors, isSubmitting }} = useForm({
    defaultValues: {
        email: "",
        password:"",
    }
})

    const onSubmit = (data) => {
        console.log(data);
    }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white mb-6 text-center">
          Sign In
        </h1>
        <p className="text-gray-600 dark:text-gray-300 text-center">
          Login stranica - u izradi
        </p>

        <form onSubmit={handleSubmit(onSubmit)}>
            <div>
                <label htmlFor="email">Email</label>
                <input className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white" type="email" id="email" {...register("email", {required: "Email is required"})}/>
                {errors.email && <p className="text-red-500">{errors.email.message}</p>}
            </div>
            <div>
                <label htmlFor="password">Password</label>
                <input className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white" type="text" id="pass" {...register("password", {required: "Password is required"})}/>
                {errors.password && <p className="text-red-500">{errors.password.message}</p>}
            </div>
            <button 
                type="submit" 
                disabled={isSubmitting} 
                className="w-full mt-4 px-4 py-2 bg-red-200 text-red-500 rounded-md hover:bg-red-300 focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
                Sign In
            </button>
        </form>
      </div>
    </div>
  );
}
