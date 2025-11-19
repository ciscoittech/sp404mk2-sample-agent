// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';
import { Box, Fab, TextField, InputAdornment } from '@mui/material';
import { IconMenu2, IconSearch } from '@tabler/icons-react';
import { EmailContext } from 'src/context/EmailContext';

interface Props {
  onClick: React.MouseEventHandler<HTMLButtonElement>;
}

const EmailSearch = ({ onClick }: Props) => {

  const { setSearchQuery, searchQuery } = useContext(EmailContext);

  const handleSearchChange = (event: { target: { value: string; }; }) => {
    const query = event.target.value.toLowerCase();
    setSearchQuery(query);
  };


  return (
    (<Box display="flex" sx={{ p: 2 }}>
      {/* ------------------------------------------- */}
      {/* Button toggle sidebar when lgdown */}
      {/* ------------------------------------------- */}
      <Fab
        onClick={onClick}
        color="primary"
        size="small"
        sx={{ mr: 1, flexShrink: '0', display: { xs: 'block', lineHeight: '10px', lg: 'none' } }}
      >
        <IconMenu2 width="16" />
      </Fab>
      {/* ------------------------------------------- */}
      {/* Search */}
      {/* ------------------------------------------- */}
      <TextField
        id="outlined-basic"
        fullWidth
        size="small"
        value={searchQuery}
        placeholder="Search emails"
        variant="outlined"
        onChange={handleSearchChange}
        slotProps={{
          input: {
            endAdornment: (
              <InputAdornment position="end">
                <IconSearch size={'16'} />
              </InputAdornment>
            ),
          }
        }}
      />
    </Box>)
  );
};

export default EmailSearch;
