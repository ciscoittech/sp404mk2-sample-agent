import * as React from 'react';
import { Box, Divider, Container } from '@mui/material';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import { styled } from '@mui/material/styles';
import { IconAppWindow, IconArrowRampLeft, IconUserCircle, IconWallet } from '@tabler/icons';
import { useTheme } from '@mui/material/styles';
import TabTeamScheduling from './TabTeamScheduling';
import TabPayments from './TabPayments';
import TabEmbedding from './TabEmbedding';
import TabWorkflows from './TabWorkflows';

const COMMON_TAB = [
  {
    value: '1',
    icon: <IconUserCircle width={20} height={20} />,
    label: 'Team Scheduling',
    disabled: false,
  },
  { value: '2', icon: <IconWallet width={20} height={20} />, label: 'Payments', disabled: false },
  {
    value: '3',
    icon: <IconAppWindow width={20} height={20} />,
    label: 'Embedding',
    disabled: true,
  },
  {
    value: '4',
    icon: <IconArrowRampLeft width={20} height={20} />,
    label: 'Workflows',
    disabled: true,
  },
];

const StyledTabPanelItem = styled(TabPanel)(() => ({
  padding: 0,
  marginTop: '85px',
}));

const DefendFocus = () => {
  const theme = useTheme();
  const borderColor = theme.palette.divider;

  const [value, setValue] = React.useState('1');

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const StyledTab = styled(Tab)(() => ({
    fontWeight: 500,
    borderRight: `1px solid ${borderColor}`,
    '& .MuiTab-icon': {
      marginRight: '12px',
      width: '24px',
      height: '24px',
      strokeWidth: '1.5px',
    },
    '&:last-child': {
      borderRight: 0,
    },
  }));

  return (
    <Box sx={{ boxShadow: (theme) => theme.shadows[10], pb: { xs: 2, lg: 4 } }}>
      <Divider />
      <Container maxWidth="lg">
        <TabContext value={value}>
          <Box sx={{ maxWidth: { xs: 400, sm: '100%' } }}>
            <TabList
              TabIndicatorProps={{
                style: {
                  top: 0,
                },
              }}
              variant="scrollable"
              allowScrollButtonsMobile
              scrollButtons="auto"
              onChange={handleChange}
              aria-label="lab API tabs example"
            >
              {COMMON_TAB.map((tab, index) => (
                <StyledTab
                  key={tab.value}
                  label={tab.label}
                  iconPosition="start"
                  icon={tab.icon}
                  value={String(index + 1)}
                  sx={{
                    fontSize: {
                      xs: '15px',
                      lg: '18px',
                    },
                    flex: {
                      xs: 'none',
                      sm: '1 1 0px',
                    },
                  }}
                />
              ))}
            </TabList>
          </Box>
          <Box mb={5}>
            <StyledTabPanelItem value="1">
              <TabTeamScheduling />
            </StyledTabPanelItem>

            <StyledTabPanelItem value="2">
              <TabPayments />
            </StyledTabPanelItem>

            <StyledTabPanelItem value="3">
              <TabEmbedding />
            </StyledTabPanelItem>

            <StyledTabPanelItem value="4">
              <TabWorkflows />
            </StyledTabPanelItem>
          </Box>
        </TabContext>
      </Container>
    </Box>
  );
};
export default DefendFocus;
