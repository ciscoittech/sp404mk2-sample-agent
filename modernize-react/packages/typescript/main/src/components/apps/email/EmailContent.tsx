// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useState, useContext } from 'react';
import {
  Box,
  Avatar,
  Typography,
  Chip,
  Button,
  Divider,
  Stack,
  IconButton,
  Grid,
  Tooltip,
  Paper,
  useTheme
} from '@mui/material';
;
import { IconStar, IconAlertCircle, IconTrash } from '@tabler/icons-react';

import emailIcon from 'src/assets/images/breadcrumb/emailSv.png';
import { EmailContext } from "src/context/EmailContext";
import TiptapEdit from 'src/views/forms/from-tiptap/TiptapEdit'


const EmailContent = () => {


  const { selectedEmail, deleteEmail, toggleStar, toggleImportant }: any =
    useContext(EmailContext);



  const handleDelete = () => {
    if (selectedEmail) {
      deleteEmail(selectedEmail.id);
    }
  };


  const [show, setShow] = useState(false);


  const toggleEditor = () => {
    setShow(!show);
  };


  const theme = useTheme();

  const warningColor = theme.palette.warning.main;
  const errorColor = theme.palette.error.light;



  return selectedEmail ? (
    <Box>
      <Stack p={2} gap={0} direction="row">
        <Tooltip title={selectedEmail.starred ? 'Unstar' : 'Star'}>
          <IconButton onClick={() => toggleStar(selectedEmail.id)}>
            <IconStar
              stroke={1.3}
              size="18"
              style={{
                fill: selectedEmail.starred ? warningColor : '',
                stroke: selectedEmail.starred ? warningColor : '',
              }}
            />
          </IconButton>
        </Tooltip>
        <Tooltip title={selectedEmail ? 'Important' : 'Not Important'}>
          <IconButton onClick={() => toggleImportant(selectedEmail.id)}>
            <IconAlertCircle
              size="18"
              stroke={1.3}
              style={{
                fill: selectedEmail.important ? errorColor : '',
              }}
            />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton onClick={handleDelete} >
            <IconTrash size="18" stroke={1.3} />
          </IconButton>
        </Tooltip>
      </Stack>
      <Divider />
      <Box p={3}>
        {/* ------------------------------------------- */}
        {/* Email Detail page */}
        {/* ------------------------------------------- */}
        <Box display="flex" alignItems="center" sx={{ pb: 3 }}>
          <Avatar alt={selectedEmail.from} src={selectedEmail.thumbnail} />
          <Box sx={{ ml: 2 }}>
            <Typography variant="h6">{selectedEmail.from}</Typography>
            <Typography variant="body2">{selectedEmail.To}</Typography>
          </Box>
          <Chip
            label={selectedEmail.label}
            sx={{ ml: 'auto', height: '21px' }}
            size="small"
            color={
              selectedEmail.label === 'Promotional'
                ? 'primary'
                : selectedEmail.label === 'Social'
                  ? 'error'
                  : 'success'
            }
          />
        </Box>
        {/* ------------------------------------------- */}
        {/* Email Detail page */}
        {/* ------------------------------------------- */}

        <Box sx={{ py: 2 }}>
          <Typography variant="h4">{selectedEmail.subject}</Typography>
        </Box>

        <Box sx={{ py: 2 }}>
          <div dangerouslySetInnerHTML={{ __html: selectedEmail.emailContent }} />
        </Box>
      </Box>
      {selectedEmail?.attchments?.length == 0 ? null : (
        <>
          <Divider />
          <Box p={3}>
            <Typography variant="h6">Attachments ({selectedEmail?.attchments?.length})</Typography>

            <Grid container spacing={3}>
              {selectedEmail.attchments?.map((attach: any) => {
                return (
                  (<Grid
                    key={attach.id}
                    size={{
                      lg: 4
                    }}>
                    <Stack direction="row" gap={2} mt={2}>
                      <Avatar
                        variant="rounded"
                        sx={{ width: '48px', height: '48px', bgcolor: (theme: any) => theme.palette.grey[100] }}
                      >
                        <Avatar
                          src={attach.image}
                          alt="av"
                          variant="rounded"
                          sx={{ width: '24px', height: '24px' }}
                        ></Avatar>
                      </Avatar>
                      <Box mr={'auto'}>
                        <Typography variant="subtitle2" fontWeight={600} mb={1}>
                          {attach.title}
                        </Typography>
                        <Typography variant="body2">{attach.fileSize}</Typography>
                      </Box>
                    </Stack>
                  </Grid>)
                );
              })}
            </Grid>
          </Box>
          <Divider />
        </>
      )}

      <Box p={3}>
        <Stack direction="row" gap={2}>
          <Button variant="outlined" size="small" color="primary" onClick={toggleEditor}>
            Reply
          </Button>
          <Button variant="outlined" size="small">
            Forward
          </Button>
        </Stack>

        {/* Editor */}
        {show ? (
          <Box mt={3}>
            <Paper variant="outlined">
              <TiptapEdit />
            </Paper>
          </Box>
        ) : null}
      </Box>
    </Box>
  ) : (
    <Box p={3} height="50vh" display={'flex'} justifyContent="center" alignItems={'center'}>
      {/* ------------------------------------------- */}
      {/* If no Email  */}
      {/* ------------------------------------------- */}
      <Box>
        <Typography variant="h4">Please Select a Mail</Typography>
        <br />
        <img src={emailIcon} alt={emailIcon} width={'250px'} />
      </Box>
    </Box>
  );
};

export default EmailContent;
