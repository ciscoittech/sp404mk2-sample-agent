import React from 'react';
import { Grid } from '@mui/material';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Divider from '@mui/material/Divider';
import Tabs from '@mui/material/Tabs';

import { TabContext, TabList, TabPanel } from '@mui/lab';

// common component
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import ParentCard from '../../components/shared/ParentCard';
import ChildCard from '../../components/shared/ChildCard';

import IconWithLabelCode from '../../components/material-ui/tabs/code/IconWithLabelCode';
import IconBottomCode from '../../components/material-ui/tabs/code/IconBottomCode';
import IconLeftCode from '../../components/material-ui/tabs/code/IconLeftCode';
import IconRightCode from '../../components/material-ui/tabs/code/IconRightCode';
import ScrollableCode from '../../components/material-ui/tabs/code/ScrollableCode';
import TextCode from '../../components/material-ui/tabs/code/TextCode';
import IconCode from '../../components/material-ui/tabs/code/IconCode';
import VerticalCode from '../../components/material-ui/tabs/code/VerticalCode';

// icon
import { IconHeart, IconPhone, IconUser } from '@tabler/icons';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Tabs',
  },
];

const COMMON_TAB = [
  { value: '1', icon: <IconPhone width={20} height={20} />, label: 'Item One', disabled: false },
  { value: '2', icon: <IconHeart width={20} height={20} />, label: 'Item Two', disabled: false },
  { value: '3', icon: <IconUser width={20} height={20} />, label: 'Item Three', disabled: true },
];

const SCROLLABLE_TAB = [
  { value: '1', icon: <IconUser width={20} height={20} />, label: 'Item 1' },
  { value: '2', icon: <IconUser width={20} height={20} />, label: 'Item 2' },
  { value: '3', icon: <IconUser width={20} height={20} />, label: 'Item 3' },
  { value: '4', icon: <IconUser width={20} height={20} />, label: 'Item 4' },
  { value: '5', icon: <IconUser width={20} height={20} />, label: 'Item 5' },
  { value: '6', icon: <IconUser width={20} height={20} />, label: 'Item 6' },
  { value: '7', icon: <IconUser width={20} height={20} />, label: 'Item 7' },
];

const MuiTabs = () => {
  const [value, setValue] = React.useState('1');

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  return (
    // 2

    (<PageContainer title="Tabs" description="this is Tabs page">
      {/* breadcrumb */}
      <Breadcrumb title="Tabs" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Tabs">
        <Grid container spacing={3}>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Text */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Text" codeModel={<TextCode />}>
              <TabContext value={value}>
                <Box>
                  <TabList
                    variant="scrollable"
                    scrollButtons="auto"
                    onChange={handleChange}
                    aria-label="lab API tabs example"
                  >
                    {COMMON_TAB.map((tab, index) => (
                      <Tab key={tab.value} label={tab.label} value={String(index + 1)} />
                    ))}
                  </TabList>
                </Box>
                <Divider />
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={String(index + 1)}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Icon */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Icon" codeModel={<IconCode />}>
              <TabContext value={value}>
                <Tabs
                  variant="scrollable"
                  scrollButtons="auto"
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                >
                  {COMMON_TAB.map((tab, index) => (
                    <Tab key={tab.value} icon={tab.icon} value={tab.value} />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Icon with Label */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Icon with Label" codeModel={<IconWithLabelCode />}>
              <TabContext value={value}>
                <Tabs
                  variant="scrollable"
                  scrollButtons="auto"
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                >
                  {COMMON_TAB.map((tab, index) => (
                    <Tab
                      key={tab.value}
                      icon={tab.icon}
                      label={tab.label}
                      value={tab.value}
                      disabled={tab.disabled}
                    />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Icon Bottom */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Icon Bottom" codeModel={<IconBottomCode />}>
              <TabContext value={value}>
                <Tabs
                  variant="scrollable"
                  scrollButtons="auto"
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                >
                  {COMMON_TAB.map((tab, index) => (
                    <Tab
                      key={tab.value}
                      icon={tab.icon}
                      label={tab.label}
                      iconPosition="bottom"
                      value={tab.value}
                      disabled={tab.disabled}
                    />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Icon Left */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Icon Left" codeModel={<IconLeftCode />}>
              <TabContext value={value}>
                <Tabs
                  variant="scrollable"
                  scrollButtons="auto"
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                >
                  {COMMON_TAB.map((tab, index) => (
                    <Tab
                      key={tab.value}
                      icon={tab.icon}
                      label={tab.label}
                      iconPosition="start"
                      value={tab.value}
                      disabled={tab.disabled}
                    />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Icon Right */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Icon Right" codeModel={<IconRightCode />}>
              <TabContext value={value}>
                <Tabs
                  variant="scrollable"
                  scrollButtons="auto"
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                >
                  {COMMON_TAB.map((tab, index) => (
                    <Tab
                      key={tab.value}
                      icon={tab.icon}
                      label={tab.label}
                      iconPosition="end"
                      value={tab.value}
                      disabled={tab.disabled}
                    />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {COMMON_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Scrollable  */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Scrollable" codeModel={<ScrollableCode />}>
              <TabContext value={value}>
                <Tabs
                  value={value}
                  onChange={handleChange}
                  aria-label="icon tabs example"
                  variant="scrollable"
                  scrollButtons="auto"
                >
                  {SCROLLABLE_TAB.map((tab, index) => (
                    <Tab
                      key={tab.value}
                      icon={tab.icon}
                      label={tab.label}
                      iconPosition="top"
                      value={tab.value}
                      disabled={tab.disabled}
                    />
                  ))}
                </Tabs>
                <Box backgroundColor="grey.100" mt={2}>
                  {SCROLLABLE_TAB.map((panel, index) => (
                    <TabPanel key={panel.value} value={panel.value}>
                      {panel.label}
                    </TabPanel>
                  ))}
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
          {/* ---------------------------------------------------------------------------------- */}
          {/* Vertical */}
          {/* ---------------------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Vertical" codeModel={<VerticalCode />}>
              <TabContext value={value}>
                <Box width="100%" gap={2} display="flex" flexGrow={1} sx={{ height: 224 }}>
                  <Tabs
                    value={value}
                    orientation="vertical"
                    onChange={handleChange}
                    variant="scrollable"
                    scrollButtons="auto"
                  >
                    {SCROLLABLE_TAB.map((tab, index) => (
                      <Tab
                        key={tab.value}
                        icon={tab.icon}
                        label={tab.label}
                        iconPosition="top"
                        value={tab.value}
                        disabled={tab.disabled}
                      />
                    ))}
                  </Tabs>
                  <Box backgroundColor="grey.100" width="100%">
                    {SCROLLABLE_TAB.map((panel, index) => (
                      <TabPanel key={panel.value} value={panel.value}>
                        {panel.label}
                      </TabPanel>
                    ))}
                  </Box>
                </Box>
              </TabContext>
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
};
export default MuiTabs;
