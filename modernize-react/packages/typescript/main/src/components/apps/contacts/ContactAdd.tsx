// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  TextField,
  FormLabel,
  DialogContent,
  DialogContentText,
  Grid,
} from '@mui/material';

import { ContactContext } from "src/context/ConatactContext";
import user1 from '../../../assets/images/profile/user-1.jpg';

const ContactAdd = () => {

  const [modal, setModal] = React.useState(false);

  const { addContact } = useContext(ContactContext);

  const toggle = () => {
    setModal(!modal);
  };

  const [values, setValues] = React.useState({
    firstname: '',
    lastname: '',
    department: '',
    company: '',
    phone: '',
    email: '',
    address: '',
    notes: '',
  });

  const handleSubmit = (e: any) => {
    e.preventDefault();

    const newContact = {
      firstname: values.firstname,
      lastname: values.lastname,
      department: values.department,
      company: values.company,
      phone: values.phone,
      email: values.email,
      address: values.address,
      notes: values.notes,
      starred: false, // Assuming default starred status is false
      image: user1, // or add a placeholder for the image
    };
    addContact(newContact);
    setModal(!modal);
  };

  return (<>
    <Box p={3} pb={1}>
      <Button color="primary" variant="contained" fullWidth onClick={toggle}>
        Add New Contact
      </Button>
    </Box>
    <Dialog
      open={modal}
      onClose={toggle}
      maxWidth="sm"
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title" variant="h5">
        {'Add New Contact'}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          Lets add new contact for your application. fill the all field and
          <br /> click on submit button.
        </DialogContentText>
        <Box mt={3}>
          <form onSubmit={handleSubmit}>
            <Grid spacing={3} container>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>FirstName</FormLabel>
                <TextField
                  id="firstname"
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.firstname}
                  onChange={(e) => setValues({ ...values, firstname: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>LastName</FormLabel>
                <TextField
                  id="lastname"
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.lastname}
                  onChange={(e) => setValues({ ...values, lastname: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>Department</FormLabel>
                <TextField
                  id="department"
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.department}
                  onChange={(e) => setValues({ ...values, department: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>Company</FormLabel>
                <TextField
                  id="company"
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.company}
                  onChange={(e) => setValues({ ...values, company: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>Phone</FormLabel>
                <TextField
                  id="phone"
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.phone}
                  onChange={(e) => setValues({ ...values, phone: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 6
                }}>
                <FormLabel>Email</FormLabel>
                <TextField
                  id="email"
                  type="email"
                  required
                  size="small"
                  variant="outlined"
                  fullWidth
                  value={values.email}
                  onChange={(e) => setValues({ ...values, email: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 12
                }}>
                <FormLabel>Address</FormLabel>
                <TextField
                  id="address"
                  size="small"
                  multiline
                  rows="3"
                  variant="outlined"
                  fullWidth
                  value={values.address}
                  onChange={(e) => setValues({ ...values, address: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 12
                }}>
                <FormLabel>Notes</FormLabel>
                <TextField
                  id="notes"
                  size="small"
                  multiline
                  rows="4"
                  variant="outlined"
                  fullWidth
                  value={values.notes}
                  onChange={(e) => setValues({ ...values, notes: e.target.value })}
                />
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  lg: 12
                }}>
                <Button
                  variant="contained"
                  color="primary"
                  sx={{ mr: 1 }}
                  type="submit"
                  disabled={values.firstname.length === 0 || values.notes.length === 0}
                >
                  Submit
                </Button>
                <Button variant="contained" color="error" onClick={toggle}>
                  Cancel
                </Button>
              </Grid>
            </Grid>
          </form>
        </Box>
      </DialogContent>
    </Dialog>
  </>);
};

export default ContactAdd;