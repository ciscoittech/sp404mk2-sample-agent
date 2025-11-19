
import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { useTheme } from '@mui/material/styles';
import { Card, CardHeader, Tooltip, Divider, IconButton } from '@mui/material';
import { CustomizerContext } from "src/context/CustomizerContext";
import { IconDownload } from '@tabler/icons';

const DownloadCard = ({ title, children, onDownload }) => {
    const { isCardShadow } = useContext(CustomizerContext);


    const theme = useTheme();
    const borderColor = theme.palette.divider;

    return (
        <Card
            sx={{ padding: 0, border: !isCardShadow ? `1px solid ${borderColor}` : 'none' }}
            elevation={isCardShadow ? 9 : 0}
            variant={!isCardShadow ? 'outlined' : undefined}
        >
            <CardHeader sx={{
                padding: "16px"
            }} title={title} action={
                <Tooltip title="Download" placement='left'>
                    <IconButton variant="contained" onClick={onDownload} >
                        <IconDownload />
                    </IconButton>
                </Tooltip>
            } />
            <Divider />
            {children}
        </Card>
    );
};
DownloadCard.propTypes = {
    title: PropTypes.string.isRequired,
    children: PropTypes.node,
    onDownload: PropTypes.func,
};
export default DownloadCard;
