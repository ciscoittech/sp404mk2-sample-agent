// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { ChangeEvent, useContext, useEffect, useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Avatar,
  Divider,
  IconButton,
  Stack,
  Grid,
  Tooltip,
  useTheme
} from '@mui/material';

import BlankCard from '../../shared/BlankCard';
import { ContactType } from 'src/types/apps/contact';
import { IconPencil, IconStar, IconTrash, IconDeviceFloppy } from '@tabler/icons-react';
import Scrollbar from 'src/components/custom-scroll/Scrollbar';
import emailIcon from 'src/assets/images/breadcrumb/emailSv.png';
import { ContactContext } from 'src/context/ConatactContext';

const ContactDetails = () => {

  const theme = useTheme();
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [formData, setFormData] = useState<ContactType | any | null>(null);


  const {
    selectedContact,
    toggleStarred,
    updateContact,
    deleteContact,
  } = useContext(ContactContext);



  const warningColor = theme.palette.warning.main;

  const tableData = [
    {
      id: 1,
      title: 'Firstname',
      alias: 'firstname',
      gdata: selectedContact ? selectedContact.firstname : '',
      type: 'text',
    },
    {
      id: 2,
      title: 'Lastname',
      alias: 'lastname',
      gdata: selectedContact ? selectedContact.lastname : '',
      type: 'text',
    },
    {
      id: 3,
      title: 'Company',
      alias: 'company',
      gdata: selectedContact ? selectedContact.company : '',
      type: 'text',
    },
    {
      id: 4,
      title: 'Department',
      alias: 'department',
      gdata: selectedContact ? selectedContact.department : '',
      type: 'text',
    },
    {
      id: 5,
      title: 'Email',
      alias: 'email',
      gdata: selectedContact ? selectedContact.email : '',
      type: 'email',
    },
    {
      id: 6,
      title: 'Phone',
      alias: 'phone',
      gdata: selectedContact ? selectedContact.phone : '',
      type: 'phone',
    },
    {
      id: 7,
      title: 'Address',
      alias: 'address',
      gdata: selectedContact ? selectedContact.address : '',
      type: 'text',
    },
    {
      id: 8,
      title: 'Notes',
      alias: 'notes',
      gdata: selectedContact ? selectedContact.notes : '',
      type: 'text',
    },
  ];

  const handleEditClick = () => {
    setIsEditMode(!isEditMode);

    // If entering edit mode, initialize formData with selected contact data
    if (!isEditMode && selectedContact) {
      setFormData({ ...selectedContact });
    }
  };


  const handleSaveClick = () => {
    if (formData) {
      updateContact(formData);
    }
    setIsEditMode(false);

  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (formData) {
      setFormData((prevData: any) => ({
        ...(prevData as ContactType),
        [name]: value,
      }));
    }
  };



  return (<>
    {/* ------------------------------------------- */}
    {/* Contact Detail Part */}
    {/* ------------------------------------------- */}
    {selectedContact && !selectedContact.deleted ? (
      <>
        {/* ------------------------------------------- */}
        {/* Header Part */}
        {/* ------------------------------------------- */}
        <Box p={3} py={2} display={'flex'} alignItems="center">
          <Typography variant="h5">Contact Details</Typography>
          <Stack gap={0} direction="row" ml={'auto'}>
            <Tooltip title={selectedContact.starred ? 'Unstar' : 'Star'}>
              <IconButton onClick={() => (toggleStarred(selectedContact?.id))}>
                <IconStar
                  stroke={1.3}
                  size="18"
                  style={{
                    fill: selectedContact.starred ? warningColor : '',
                    stroke: selectedContact.starred ? warningColor : '',
                  }}
                />
              </IconButton>
            </Tooltip>
            <Tooltip title={!isEditMode ? "Edit" : "Save"}>
              <IconButton onClick={isEditMode ? handleSaveClick : handleEditClick}>
                {!isEditMode ? (
                  <IconPencil size="18" stroke={1.3} />
                ) : (
                  <IconDeviceFloppy size="18" stroke={1.3} />
                )}
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton onClick={() => deleteContact(selectedContact.id)}>
                <IconTrash size="18" stroke={1.3} />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>
        <Divider />
        {/* ------------------------------------------- */}
        {/* Contact Table Part */}
        {/* ------------------------------------------- */}
        <Box sx={{ overflow: 'auto' }}>
          {!isEditMode ? (
            <Box>
              <Box p={3}>
                <Box display="flex" alignItems="center">
                  <Avatar
                    alt={selectedContact.image}
                    src={selectedContact.image}
                    sx={{ width: '72px', height: '72px' }}
                  />
                  <Box sx={{ ml: 2 }}>
                    <Typography variant="h6" mb={0.5}>
                      {selectedContact.firstname} {selectedContact.lastname}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={0.5}>
                      {selectedContact.department}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedContact.company}
                    </Typography>
                  </Box>
                </Box>
                <Grid container>
                  <Grid
                    mt={4}
                    size={{
                      lg: 6,
                      xs: 12
                    }}>
                    <Typography variant="body2" color="text.secondary">
                      Phone Number
                    </Typography>
                    <Typography variant="subtitle1" mb={0.5} fontWeight={600}>
                      {selectedContact.phone}
                    </Typography>
                  </Grid>
                  <Grid
                    mt={4}
                    size={{
                      lg: 6,
                      xs: 12
                    }}>
                    <Typography variant="body2" color="text.secondary">
                      Email address
                    </Typography>
                    <Typography variant="subtitle1" fontWeight={600} mb={0.5}>
                      {selectedContact.email}
                    </Typography>
                  </Grid>
                  <Grid
                    mt={4}
                    size={{
                      lg: 12,
                      xs: 12
                    }}>
                    <Typography variant="body2" color="text.secondary">
                      Address
                    </Typography>
                    <Typography variant="subtitle1" fontWeight={600} mb={0.5}>
                      {selectedContact.address}
                    </Typography>
                  </Grid>
                  <Grid
                    mt={4}
                    size={{
                      lg: 6,
                      xs: 12
                    }}>
                    <Typography variant="body2" color="text.secondary">
                      Department
                    </Typography>
                    <Typography variant="subtitle1" mb={0.5} fontWeight={600}>
                      {selectedContact.department}
                    </Typography>
                  </Grid>
                  <Grid
                    mt={4}
                    size={{
                      lg: 6,
                      xs: 12
                    }}>
                    <Typography variant="body2" color="text.secondary">
                      Company
                    </Typography>
                    <Typography variant="subtitle1" fontWeight={600} mb={0.5}>
                      {selectedContact.company}
                    </Typography>
                  </Grid>
                  <Grid
                    mt={4}
                    size={{
                      lg: 12,
                      xs: 12
                    }}>
                    <Typography variant="body2" mb={1} color="text.secondary">
                      Notes
                    </Typography>
                    <Typography variant="subtitle1" mb={0.5}>
                      {selectedContact.notes}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
              <Divider />
              <Box p={3} gap={1} display="flex">
                <Button
                  color="primary"
                  variant="contained"
                  size="small"
                  onClick={handleEditClick}
                >
                  Edit
                </Button>
                <Button
                  color="error"
                  variant="contained"
                  size="small"
                  onClick={() => deleteContact(selectedContact.id)}
                >
                  Delete
                </Button>
              </Box>
            </Box>
          ) : (
            <>
              <BlankCard sx={{ p: 0 }}>
                <Scrollbar sx={{ height: { lg: 'calc(100vh - 360px)', md: '100vh' } }}>
                  <Box pt={1}>
                    {tableData.map((data) => (
                      <Box key={data.id} px={3} py={1.5}>
                        <Typography variant="subtitle1" fontWeight={600} mb={0.5}>
                          {data.title}
                        </Typography>
                        <TextField
                          id={data.alias}
                          size="small"
                          fullWidth
                          type={data.type}
                          name={data.alias}
                          value={formData ? formData[data.alias] : ''}

                          onChange={handleInputChange}
                        />

                      </Box>
                    ))}
                    <Box p={3}>
                      <Button
                        color="primary"
                        variant="contained"
                        onClick={handleSaveClick}
                      >
                        Save Contact
                      </Button>
                    </Box>
                  </Box>
                </Scrollbar>
              </BlankCard>
            </>
          )}
        </Box>
      </>
    ) : (
      <Box p={3} height="50vh" display={'flex'} justifyContent="center" alignItems={'center'}>
        {/* ------------------------------------------- */}
        {/* If no Contact  */}
        {/* ------------------------------------------- */}
        <Box>
          <Typography variant="h4">Please Select a Contact</Typography>
          <br />
          <img src={emailIcon} alt={emailIcon} width={'250px'} />
        </Box>
      </Box>
    )}
  </>);
};

export default ContactDetails;