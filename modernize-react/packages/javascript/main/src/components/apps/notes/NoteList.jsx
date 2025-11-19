// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext, useEffect, useState } from 'react';
import { IconButton, Box, Stack, Typography, TextField, Tooltip, Alert } from '@mui/material';
import Scrollbar from '../../custom-scroll/Scrollbar';
import { IconTrash } from '@tabler/icons-react';
import { NotesContext } from "src/context/NotesContext";

const NoteList = () => {

  const { notes, selectNote, deleteNote } = useContext(NotesContext);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeNoteId, setActiveNoteId] = useState(null);
  useEffect(() => {
    if (notes.length > 0) {
      // Set the first note as active 
      const firstNoteId = notes[0].id;
      setActiveNoteId(firstNoteId);
    }
  }, [notes]);


  const filterNotes = (notes, nSearch) => {
    if (nSearch !== "")
      return notes.filter(
        (t) =>
          !t.deleted &&
          t.title
            .toLocaleLowerCase()
            .concat(" ")
            .includes(nSearch.toLocaleLowerCase())
      );

    return notes.filter((t) => !t.deleted);
  };

  const filteredNotes = filterNotes(notes, searchTerm);

  const handleNoteClick = (noteId) => {
    setActiveNoteId(noteId);
    selectNote(noteId);
  };


  return (<>
    <Box p={3} px={2}>
      <TextField
        id="search"
        value={searchTerm}
        placeholder="Search Notes"
        size="small"
        type="search"
        variant="outlined"
        fullWidth
        onChange={(e) => setSearchTerm(e.target.value)}
        slotProps={{
          htmlInput: { 'aria-label': 'Search Notes' }
        }}
      />
      <Typography variant="h6" mb={0} mt={4} pl={1}>
        All Notes
      </Typography>
    </Box>
    <Box>
      <Scrollbar sx={{ height: { lg: 'calc(100vh - 300px)', sm: '100vh' }, maxHeight: '700px' }}>
        {filteredNotes && filteredNotes.length ? (
          filteredNotes.map((note) => (
            <Box key={note.id} px={2}>
              <Box
                p={2}
                sx={{
                  position: 'relative',
                  cursor: 'pointer',
                  mb: 1,
                  transition: '0.1s ease-in',
                  transform: activeNoteId === note.id ? 'scale(1)' : 'scale(0.95)',
                  backgroundColor: `${note.color}.light`,

                }}
                onClick={() => handleNoteClick(note.id)}
              >
                <Typography variant="h6" noWrap color={note.color + '.main'}>
                  {note.title}
                </Typography>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption">
                    {new Date(note.datef).toLocaleDateString()}
                  </Typography>
                  <Tooltip title="Delete">
                    <IconButton
                      aria-label="delete"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNote(note.id);
                      }}
                    >
                      <IconTrash width={18} />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </Box>
            </Box>
          ))
        ) : (
          <Box m={2}>
            <Alert severity="error" variant="filled" sx={{ color: 'white' }}>
              No Notes Found!
            </Alert>
          </Box>
        )}
      </Scrollbar>
    </Box>
  </>);
};

export default NoteList;
