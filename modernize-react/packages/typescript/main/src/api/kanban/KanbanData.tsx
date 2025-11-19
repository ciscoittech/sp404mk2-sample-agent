import { TodoCategory } from '../../types/apps/kanban';

import img1 from '../../assets/images/kanban/kanban-img-1.jpg';
import img2 from '../../assets/images/kanban/kanban-img-2.jpg';
import img3 from '../../assets/images/kanban/kanban-img-3.jpg';
import img4 from '../../assets/images/kanban/kanban-img-4.jpg';
import { http, HttpResponse } from 'msw';

const KanbanData: TodoCategory[] = [
  {
    id: '1',
    name: 'Todo',
    child: [
      {
        id: '101',
        task: 'This is first task',
        taskImage: img1,
        taskText: '',
        date: '24 july',
        taskProperty: 'Design',
      },
      {
        id: '102',
        task: 'lets do some task on pd',
        taskImage: '',
        taskText:
          'Lorem ipsum dolor sit amet, consectetur adipisicing elit, o eiusmod tempor incid.',
        date: '24 july',
        taskProperty: 'Mobile',
      },
      {
        id: '103',
        task: 'Do some projects on React Native with Flutter',
        taskImage: '',
        taskText: '',
        date: '24 july',
        taskProperty: 'Mobile',
      },
    ],
  },
  {
    id: '2',
    name: 'Progress',
    child: [
      {
        id: '104',
        task: 'Design navigation changes',
        taskImage: '',
        taskText: '',
        date: '24 july',
        taskProperty: 'Mobile',
        category: '',
      },
      {
        id: '105',
        task: 'Battle with fire',
        taskImage: img2,
        taskText: '',
        date: '24 july',
        taskProperty: 'Design',
        category: '',
      },
      {
        id: '106',
        task: 'First design concept',
        taskImage: '',
        taskText: '',
        date: '24 july',
        taskProperty: 'Mobile',
        category: '',
      },
    ],
  },
  {
    id: '3',
    name: 'Pending',
    child: [
      {
        id: '107',
        task: 'Persona development',
        taskImage: '',
        taskText:
          'Create user personas based on the research data to represent different user groups and their characteristics, gols, and behaviors..',
        date: '24 july',
        taskProperty: 'UX Stage',
        category: 'Pending',
      },
      {
        id: '108',
        task: 'Redesign overview',
        taskImage: img3,
        taskText: '',
        date: '14 july',
        taskProperty: 'Design',
        category: 'Pending',
      },
    ],
  },
  {
    id: '4',
    name: 'Done',
    child: [
      {
        id: '109',
        task: 'Usability testing',
        taskImage: img4,
        taskText: '',
        date: '24 july',
        taskProperty: 'Research',
        category: 'Done',
      },
      {
        id: '110',
        task: 'Introduce new navigation',
        taskImage: '',
        taskText: '',
        date: '24 july',
        taskProperty: 'Data Science',
        category: 'Done',
      },
      {
        id: '111',
        task: 'Branding visual identity',
        taskImage: '',
        taskText: '',
        date: '4 july',
        taskProperty: 'Branding',
        category: 'Done',
      },
      {
        id: '112',
        task: 'Competitor research',
        taskImage: '',
        taskText:
          'research competitors and identify weakness and strengths each of them. comparing their product features, quelity...',
        date: '14 july',
        taskProperty: 'UX Stage',
        category: 'Done',
      },
    ],
  },
];

// Extracting unique task properties from TodoData
const taskPropertiesSet = new Set<string>();

// Using forEach loops instead of flatMap
KanbanData.forEach((category) => {
  category.child.forEach((task) => {
    taskPropertiesSet.add(task.taskProperty);
  });
});

// Convert Set to array
export const TaskProperties = Array.from(taskPropertiesSet);

export default KanbanData;



export const Kanbanhandlers = [

  // Mock API endpoint to fetch TodoData
  http.get('/api/kanban', () => {

    try {
      return HttpResponse.json({ status: 200, msg: "success", data: KanbanData });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  }),

  // Mock API endpoint to delete a task
  http.delete('/api/TodoData/deleteTask', async ({ request }) => {
    try {
      const { taskId } = await request.json() as { taskId: number };
      const updatedTodoData = KanbanData.filter((task) => task.id !== taskId);
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: updatedTodoData,
      });
    } catch (error) {
      return HttpResponse.json({ status: 400, msg: "failed", error });
    }
  }),

  // Mock API endpoint to add a new category
  http.post('/api/kanban/add-category', async ({ request }) => {
    try {
      const { categoryName } = await request.json() as { categoryName: string };
      const newCategory = {
        id: Math.random(),
        name: categoryName,
        child: [],
      };
      KanbanData.push(newCategory);
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: newCategory,
      });
    } catch (error) {
      return HttpResponse.json({ status: 400, msg: "failed", error });
    }
  }),

  // Mock API endpoint to delete a category
  http.delete('/api/kanban/delete-category', async ({ request }) => {
    try {
      const { id } = await request.json() as { id: number };
      const updatedTodoData = KanbanData.filter((category) => category.id !== id);
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: updatedTodoData,
      });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  }),
  // Mock API endpoint to edit a task
  http.patch('/api/kanban/edit-task', async ({ request }) => {
    try {
      const { taskId, newData } = await request.json() as { taskId: number, newData: any };
      KanbanData.forEach((category) => {
        category.child.forEach((task) => {
          if (task.id === taskId) {
            Object.assign(task, newData);
          }
        });
      });
      return HttpResponse.json({ status: 200, msg: "success", data: KanbanData });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  }),

  // Mock API endpoint to clear all tasks from a category
  http.delete('/api/TodoData/clearTasks', async ({ request }) => {
    try {
      const { categoryId } = await request.json() as { categoryId: number };
      const updatedTodoData = KanbanData.map((category) => {
        if (category.id === categoryId) {
          return { ...category, child: [] };
        }
        return category;
      });
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: updatedTodoData,
      });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  }),


  // Mock API endpoint to add a new task
  http.post('/api/TodoData/addTask', async ({ request }) => {
    try {
      const { categoryId, newTaskData } = await request.json() as { categoryId: number, newTaskData: any };
      const updatedTodoData = KanbanData.map((category) => {
        if (category.id === categoryId) {
          return { ...category, child: [...category.child, newTaskData] };
        }
        return category;
      });
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: updatedTodoData,
      });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  }),


  // Mock API endpoint to update the name of a category
  http.post('/api/TodoData/updateCategory', async ({ request }) => {
    try {
      const { categoryId, categoryName } = await request.json() as { categoryId: number, categoryName: string };
      const updatedTodoData = KanbanData.map((category) => {
        if (category.id === categoryId) {
          return { ...category, name: categoryName };
        }
        return category;
      });
      return HttpResponse.json({
        status: 200,
        msg: "success",
        data: updatedTodoData,
      });
    } catch (error) {
      return HttpResponse.json({
        status: 400,
        msg: "Internal server error",
        error,
      });
    }
  })

]