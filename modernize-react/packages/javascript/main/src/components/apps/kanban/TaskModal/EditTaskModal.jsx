

import { useEffect, useState } from 'react';
import { TaskProperties } from '../../../../api/kanban/KanbanData';
import {
  Button,

  MenuItem,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
} from '@mui/material';
import Dialog from '@mui/material/Dialog';
import CustomFormLabel from 'src/components/forms/theme-elements/CustomFormLabel';
import CustomTextField from 'src/components/forms/theme-elements/CustomTextField';
import CustomSelect from 'src/components/forms/theme-elements/CustomSelect';

function EditTaskModal({ show, onHide, editedTask, onSave }) {
  const [tempEditedTask, setTempEditedTask] = useState(editedTask);
  const [newImageUrl, setNewImageUrl] = useState(editedTask.taskImage || "");
  const [imagePreview, setImagePreview] = useState(editedTask.taskImage || "");

  useEffect(() => {

    setTempEditedTask({
      ...editedTask,
    });
    setNewImageUrl(editedTask.taskImage || "");
    setImagePreview(editedTask.taskImage || "");
  }, [editedTask]);


  // Function to handle changes in the task input fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setTempEditedTask({ ...tempEditedTask, [name]: value });
  };

  // Function to handle changes in the task property
  const handlePropertyChange = (property) => {
    setTempEditedTask({ ...tempEditedTask, taskProperty: property });
  };

  // Function to handle saving the changes made to the task and hiding the modal
  const handleSaveChanges = () => {
    const updatedTask = { ...tempEditedTask, taskImage: newImageUrl };
    onSave(updatedTask);
    onHide();
  };



  // Function to handle new image URL input
  const handleNewImageUrlChange = (e) => {
    const url = e.target.value;
    setNewImageUrl(url);
    setImagePreview(url); // Update the preview with the new image URL
  };

  return (
    <Dialog
      open={show}
      onClose={onHide}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"

      slotProps={{
        paper: {
          component: 'form',
        },
      }}
    >
      <DialogTitle id="alert-dialog-title">Edit Task</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            {/* Task title */}
            <CustomFormLabel sx={{ mt: 0 }} htmlFor="task">
              Task Title
            </CustomFormLabel>
            <CustomTextField
              id="task"
              name="task"
              variant="outlined"
              fullWidth
              value={tempEditedTask.task}
              onChange={handleChange}
            />
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            {/* Task property */}
            <CustomFormLabel htmlFor="taskProperty" sx={{ mt: 0 }}>
              Task Property *
            </CustomFormLabel>
            <CustomSelect
              fullWidth
              id="taskProperty"
              variant="outlined"
              value={tempEditedTask.taskProperty}
              onChange={(e) => handlePropertyChange(e.target.value)}
            >
              {TaskProperties.map((property) => (
                <MenuItem key={property} value={property}>
                  {property}
                </MenuItem>
              ))}
            </CustomSelect>
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6
            }}>
            {/* Task text or image */}
            {tempEditedTask.taskImage ? (
              <>
                {/* Image handling */}
                <CustomFormLabel htmlFor="taskImage" sx={{ mt: 0 }}>
                  Image URL
                </CustomFormLabel>
                <CustomTextField
                  id="taskImage"
                  variant="outlined"
                  fullWidth
                  value={newImageUrl}
                  onChange={handleNewImageUrlChange}
                />
                {imagePreview && (
                  <Grid sx={{ mt: 2 }} size={12}>
                    <CustomFormLabel htmlFor="taskImage">Image Preview:</CustomFormLabel>
                    <img
                      src={imagePreview}
                      alt="Selected"
                      style={{ maxWidth: '100%', height: 'auto', marginTop: '8px', borderRadius: "4px" }}

                    />
                  </Grid>
                )}
              </>
            ) : (
              <>
                {/* Task text */}
                <CustomFormLabel sx={{ mt: 0 }} htmlFor="task-text">
                  Text
                </CustomFormLabel>
                <CustomTextField
                  id="task-text"
                  variant="outlined"
                  fullWidth
                  name="taskText"
                  value={tempEditedTask.taskText}
                  onChange={handleChange}
                />
              </>
            )}
          </Grid>


        </Grid>
      </DialogContent>
      <DialogActions>
        <Button variant="outlined" color="error" onClick={onHide}>
          Close
        </Button>
        <Button variant="contained" onClick={handleSaveChanges} autoFocus>
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default EditTaskModal;