import { useTheme } from '@mui/material/styles';
import { Card, CardHeader, Tooltip, Divider, IconButton } from '@mui/material';
import { useContext } from 'react';
import { IconDownload } from '@tabler/icons-react';
import { CustomizerContext } from "src/context/CustomizerContext";

const DownloadCard = ({ title, children, onDownload }: any) => {


  const theme = useTheme();
  const borderColor = theme.palette.divider;
  const { isCardShadow } = useContext(CustomizerContext);

  return (
    <Card
      sx={{ padding: 0, border: !isCardShadow ? `1px solid ${borderColor}` : 'none' }}
      elevation={isCardShadow ? 9 : 0}
      variant={!isCardShadow ? 'outlined' : undefined}
    >
      <CardHeader
        sx={{
          padding: '16px',
        }}
        title={title}
        action={
          <Tooltip title="Download" placement="left">
            <IconButton onClick={onDownload}>
              <IconDownload />
            </IconButton>
          </Tooltip>
        }
      />
      <Divider />
      {children}
    </Card>
  );
};

export default DownloadCard;
