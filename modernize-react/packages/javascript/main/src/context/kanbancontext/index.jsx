import React, { createContext, useState, useEffect } from 'react';
import { deleteFetcher, getFetcher, postFetcher } from 'src/api/globalFetcher';
import useSWR from 'swr';





export const KanbanDataContext = createContext({});

export const KanbanDataContextProvider = ({ children }) => {
    const [todoCategories, setTodoCategories] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true)

    // Fetch todo data from the API
    const { data: todosData, isLoading: isTodosLoading, error: todoError, mutate } = useSWR("/api/kanban", getFetcher,)
    useEffect(() => {
        if (todosData) {
            setTodoCategories(todosData.data);
            setLoading(isTodosLoading);
        } else if (todoError) {
            setError(todoError);
            setLoading(isTodosLoading);
        } else {
            setLoading(isTodosLoading);
        }
    }, [todosData, todoError, isTodosLoading]);



    const moveTask = (_, sourceCategoryId, destinationCategoryId, sourceIndex, destinationIndex) => {

        setTodoCategories((prevCategories) => {
            // Find the source and destination categories
            const sourceCategoryIndex = prevCategories.findIndex(cat => cat.id.toString() === sourceCategoryId);
            const destinationCategoryIndex = prevCategories.findIndex(cat => cat.id.toString() === destinationCategoryId);

            if (sourceCategoryIndex === -1 || destinationCategoryIndex === -1) {
                return prevCategories; // Return previous state if categories are not found
            }
            // Clone the source and destination categories
            const updatedCategories = [...prevCategories];
            const sourceCategory = { ...updatedCategories[sourceCategoryIndex] };
            const destinationCategory = { ...updatedCategories[destinationCategoryIndex] };

            // Remove the task from the source category
            const taskToMove = sourceCategory.child.splice(sourceIndex, 1)[0];

            // Insert the task into the destination category at the specified index
            destinationCategory.child.splice(destinationIndex, 0, taskToMove);

            // Update the categories in the state
            updatedCategories[sourceCategoryIndex] = sourceCategory;
            updatedCategories[destinationCategoryIndex] = destinationCategory;

            return updatedCategories;
        });
    };

    const handleError = (errorMessage) => {
        setError(errorMessage);
    };

    const deleteCategory = async (categoryId) => {
        try {
            await mutate(deleteFetcher('/api/kanban/delete-category', { data: { categoryId } }), false)
        } catch (error) {
            handleError(error);
        }
    };

    const clearAllTasks = async (categoryId) => {
        try {
            await mutate(deleteFetcher('/api/TodoData/clearTasks', { data: { categoryId } }), false)
        } catch (error) {
            handleError(error);
        }
    };

    const addCategory = async (categoryName) => {
        try {
            const response = await mutate(postFetcher('/api/kanban/add-category', { categoryName }), false);
            setTodoCategories([...todoCategories, response.data]);
        } catch (error) {
            handleError(error);
        }
    };

    const deleteTodo = async (taskId) => {
        try {
            await mutate(deleteFetcher('/api/TodoData/deleteTask', { data: { taskId } }), false)
        } catch (error) {
            handleError(error);
        }
    };

    return (
        <KanbanDataContext.Provider value={{ todoCategories, loading, error, setTodoCategories, addCategory, deleteCategory, clearAllTasks, deleteTodo, setError, moveTask }}>
            {children}
        </KanbanDataContext.Provider>
    );
};