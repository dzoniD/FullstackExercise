export default function Task({ task, onEdit }) {  
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow duration-300 border border-gray-200 dark:border-gray-700 relative">
            <button
                onClick={() => onEdit(task)}
                className="absolute top-4 right-4 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="Izmeni tiket"
            >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
            </button>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-3 pr-8">
                {task.title}
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {task.description}
            </p>
        </div>
    )
  }