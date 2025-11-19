// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import Chart from 'react-apexcharts';
import { Grid } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import PageContainer from '../../components/container/PageContainer';
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import ParentCard from '../../components/shared/ParentCard';
import { Props } from 'react-apexcharts';

import RadialbarChartsCode from 'src/components/charts/Radialbar Charts/code/RadialbarChartsCode';
import RadarChartsCode from 'src/components/charts/Radar Charts/code/RadarChartsCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Radialbar Chart',
  },
];

const RadialbarChart = () => {

  // chart color
  const theme = useTheme();
  const primary = theme.palette.primary.main;
  const secondary = theme.palette.secondary.main;
  const success = theme.palette.success.main;
  const warning = theme.palette.warning.main;

  const optionsradialchart: Props = {
    chart: {
      id: 'pie-chart',
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      foreColor: '#adb0bb',
      toolbar: {
        show: false,
      },
    },
    colors: [primary, secondary, success, warning],
    plotOptions: {
      radialBar: {
        dataLabels: {
          name: {
            fontSize: '22px',
          },
          value: {
            fontSize: '16px',
          },
          total: {
            show: true,
            label: 'Total',
            formatter() {
              return 249;
            },
          },
        },
      },
    },
    tooltip: {
      theme: 'dark',
    },
  };
  const seriesradialchart: any = [44, 55, 67, 83];

  // 2
  const optionsradarchart: Props = {
    chart: {
      id: 'pie-chart',
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      toolbar: {
        show: false,
      },
    },
    colors: [primary],
    labels: ['January', 'February', 'March', 'April', 'May', 'June'],
    tooltip: {
      theme: 'dark',
    },
  };
  const seriesradarchart: any = [
    {
      name: 'Sales',
      data: [80, 50, 30, 40, 100, 20],
    },
  ];

  return (
    (<PageContainer title="Radialbar & Radar Chart" description="this is innerpage">
      {/* breadcrumb */}
      <Breadcrumb title="Radialbar Chart" items={BCrumb} />
      {/* end breadcrumb */}
      <Grid container spacing={3}>
        <Grid
          size={{
            lg: 6,
            md: 12,
            xs: 12
          }}>
          <ParentCard title="Radialbar Charts" codeModel={<RadialbarChartsCode />}>
            <Chart
              options={optionsradialchart}
              series={seriesradialchart}
              type="radialBar"
              height="338px"
            />
          </ParentCard>
        </Grid>
        <Grid
          size={{
            lg: 6,
            md: 12,
            xs: 12
          }}>
          <ParentCard title="Radar Charts" codeModel={<RadarChartsCode />}>
            <Chart
              options={optionsradarchart}
              series={seriesradarchart}
              type="radar"
              height="300px"
            />
          </ParentCard>
        </Grid>
      </Grid>
    </PageContainer>)
  );
};

export default RadialbarChart;