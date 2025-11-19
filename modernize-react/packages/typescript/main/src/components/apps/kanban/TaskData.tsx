
import { useContext, useEffect, useState } from 'react';
import { IconPencil, IconDotsVertical, IconTrash, IconCalendar } from '@tabler/icons-react';
import EditTaskModal from './TaskModal/EditTaskModal';
import { KanbanDataContext } from 'src/context/kanbancontext/index';
import { Draggable } from '@hello-pangea/dnd';
import { patchFetcher } from "src/api/globalFetcher";
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import {
  Box,
  Chip,
  IconButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography,
} from '@mui/material';
import BlankCard from '../../shared/BlankCard';
import dayjs from 'dayjs';
import { mutate } from 'swr';

interface TaskDataProps {
  task: { id: any };
  onDeleteTask: () => void;
  index: number;
  category: any;

}
const TaskData: React.FC<TaskDataProps> = ({ task, onDeleteTask, index, category }: any) => {
  const { setError, todoCategories, setTodoCategories } = useContext(KanbanDataContext);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editedTask, setEditedTask] = useState(task);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleShowEditModal = () => {
    handleClose();
    setShowEditModal(true);
  };
  const handleCloseEditModal = () => setShowEditModal(false);

  const handleClick = (event: any) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDeleteClick = () => onDeleteTask(task.id);

  const handleSaveEditedTask = async (editedTaskData: { id: any }) => {
    try {
      const response = await mutate('/api/kanban/edit-task', patchFetcher("/api/kanban/edit-task", {
        taskId: editedTaskData.id,
        newData: editedTaskData,
      }), false);
      if (response.status === 200) {
        setEditedTask(editedTaskData);
        let remainingTodos = todoCategories.map((item) => {
          if (item.name === category.name) {
            let updatedChild = item.child.map((task) => {
              if (task.id === editedTaskData.id) {
                return { ...task, editedTaskData }
              } return task
            });
            return { id: item.id, name: item.name, child: updatedChild }
          } else {
            return item
          }
        });
        setTodoCategories(remainingTodos);
      } else {
        throw new Error("Failed to edit task");
      }
    } catch (error: any) {
      setError(error.message);
    }
  };

  // Function to format the date as 'DD MMM' (Day and Month)
  const formatDate = (date: string | undefined) => {
    if (date) {
      // If the date is provided, format it to 'DD MMM' (Day and Month)
      const parsedDate = dayjs(date, "DD MMMM", true); // strict parsing mode
      if (parsedDate.isValid()) {
        return parsedDate.format("DD MMM");
      } else {
        // If invalid, try to append the current year
        const currentYear = dayjs().year();
        const newDate = `${date} ${currentYear}`; // Example: '24 july 2025'
        const correctedDate = dayjs(newDate, "DD MMMM YYYY");
        return correctedDate.isValid() ? correctedDate.format("DD MMM") : dayjs().format("DD MMM");
      }
    } else {
      // If the date is not provided, return today's date in 'DD MMM' format
      return dayjs().format("DD MMM");
    }
  };

  useEffect(() => {

  }, [editedTask])


  const taskDate = formatDate(editedTask?.date); // Get formatted task date

  const backgroundColor =
    editedTask?.taskProperty === 'Design'
      ? 'success.main'
      : editedTask?.taskProperty === 'Development'
        ? 'warning.main'
        : editedTask?.taskProperty === 'Mobile'
          ? 'primary.main'
          : editedTask?.taskProperty === 'UX Stage'
            ? 'warning.main'
            : editedTask?.taskProperty === 'Research'
              ? 'secondary.main'
              : editedTask?.taskProperty === 'Data Science'
                ? 'error.main'
                : editedTask?.taskProperty === 'Branding'
                  ? 'success.main'
                  : 'primary.contrastText';

  return (
    <Draggable draggableId={String(task?.id)} index={index}>
      {(provided: any) => (
        <Box
          mb={3}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          ref={provided.innerRef}
        >
          <BlankCard>
            <Box px={2} py={1} display="flex" alignItems="center" justifyContent="space-between">
              <Typography fontSize="14px" variant="h6">
                {editedTask?.task}
              </Typography>
              <Box>
                <IconButton
                  aria-label="more"
                  aria-controls="long-menu"
                  aria-haspopup="true"
                  onClick={handleClick}
                >
                  <IconDotsVertical size="1rem" />
                </IconButton>
                <Menu
                  id="long-menu"
                  anchorEl={anchorEl}
                  keepMounted
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                >
                  <MenuItem onClick={handleShowEditModal}>
                    <ListItemIcon>
                      <IconPencil size="1.2rem" />
                    </ListItemIcon>
                    <ListItemText> Edit</ListItemText>
                  </MenuItem>
                  <MenuItem onClick={handleDeleteClick}>
                    <ListItemIcon>
                      <IconTrash size="1.2rem" />{' '}
                    </ListItemIcon>
                    <ListItemText> Delete</ListItemText>
                  </MenuItem>
                </Menu>
                <EditTaskModal
                  show={showEditModal}
                  onHide={handleCloseEditModal}
                  task={task}
                  editedTask={editedTask}
                  onSave={handleSaveEditedTask}
                />
              </Box>
            </Box>
            <Box>
              {editedTask?.taskImage && (
                <img
                  src={editedTask?.taskImage}
                  alt="Task Image"
                  className="img-fluid"

                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              )}
            </Box>
            {editedTask?.taskText && (
              <Box px={2} py={1}>
                <Typography variant="body2">{editedTask?.taskText}</Typography>
              </Box>
            )}
            <Box display="flex" alignItems="center" justifyContent="space-between" px={2} py={1}>
              <Stack direction="row" gap={1}>
                <IconCalendar size="1rem" />
                <Typography variant="body2">  {taskDate}</Typography>
              </Stack>
              <Box>
                <Chip
                  size="small"
                  label={editedTask?.taskProperty}
                  sx={{
                    backgroundColor,
                    color: 'white',
                    borderRadius: '8px',
                    fontSize: '11px',
                    fontWeight: 400,
                  }}
                />
              </Box>
            </Box>
          </BlankCard>
        </Box>
      )}
    </Draggable>
  );
};
export default TaskData;
