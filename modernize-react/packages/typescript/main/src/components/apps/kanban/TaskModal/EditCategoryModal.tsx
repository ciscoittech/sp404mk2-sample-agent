
import { useState } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, Grid, DialogActions } from '@mui/material';
import CustomFormLabel from 'src/components/forms/theme-elements/CustomFormLabel';
import CustomTextField from 'src/components/forms/theme-elements/CustomTextField';

function EditCategoryModal({
  showModal,
  handleCloseModal,
  handleUpdateCategory,
  initialCategoryName,
}: any) {
  const [newCategoryName, setNewCategoryName] = useState(initialCategoryName || '');

  // Function to handle saving changes and updating category name
  const handleSave = () => {
    handleUpdateCategory(newCategoryName);
    handleCloseModal();
  };


  return (
    <Dialog
      open={showModal}
      onClose={handleCloseModal}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
      sx={{ ".MuiDialog-paper": { width: "600px" } }}
    >
      <DialogTitle id="alert-dialog-title">Edit Category</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid size={12}>
            {/* category title */}
            <CustomFormLabel htmlFor="cname">Category name</CustomFormLabel>
            <CustomTextField
              id="cname"
              variant="outlined"
              fullWidth
              value={newCategoryName}
              onChange={(e: any) => setNewCategoryName(e.target.value)}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button variant="outlined" color="error" onClick={handleCloseModal}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSave} autoFocus>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
export default EditCategoryModal;
