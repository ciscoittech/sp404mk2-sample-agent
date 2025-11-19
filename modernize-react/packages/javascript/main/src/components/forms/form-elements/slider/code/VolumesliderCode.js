import CodeDialog from '../../../../shared/CodeDialog';

const VolumesliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { styled } from '@mui/material/styles';
import { Slider } from '@mui/material';
import { IconVolume, IconVolume2 } from '@tabler/icons';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const CustomSlider = styled(Slider)(({ theme }) => ({
  '& .MuiSlider-rail': {
    height: '9px',
    borderRadius: '9px',
    opacity: '1',
    backgroundColor: theme.palette.grey[200],
  },
  '& .MuiSlider-thumb': {
    borderRadius: '50%',
    backgroundColor: () => theme.palette.secondary.main,
    width: '23px',
    height: '23px',
  },
  '& .MuiSlider-track': {
    height: '9px',
    borderRadius: '9px',
  },
}));

<CustomSlider defaultValue={30} aria-label="volume slider" />
<Box display="flex" alignItems="center">
    <Typography>
        <IconVolume2 width={20} />
    </Typography>
    <Box ml="auto">
        <Typography>
            <IconVolume width={20} />
        </Typography>
    </Box>
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default VolumesliderCode;
