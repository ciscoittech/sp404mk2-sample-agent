import CodeDialog from 'src/components/shared/CodeDialog';
const TextInfoCode = () => {
  return (
    <>
      <CodeDialog>
        {`

import { Typography } from '@mui/material';

<Typography variant="body1" sx={{ color: (theme) => theme.palette.info.main }}>
    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
</Typography>`}
      </CodeDialog>
    </>
  );
};

export default TextInfoCode;
