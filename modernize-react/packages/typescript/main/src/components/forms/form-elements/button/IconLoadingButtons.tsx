
import { Stack } from '@mui/material';
import { IconTrash } from '@tabler/icons-react';
import Button from '@mui/material/Button';

const IconLoadingButtons = () => (
  <Stack spacing={1} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
    <Button loading loadingIndicator="Loading…"
      variant="contained"
      color="error"
      startIcon={<IconTrash width={18} />}
    >
      Left Icon
    </Button >
    <Button loading
      variant="contained"
      color="secondary"
      endIcon={<IconTrash width={18} />}
    >
      Right Icon
    </Button >
  </Stack>
);

export default IconLoadingButtons;
