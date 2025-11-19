import CodeDialog from 'src/components/shared/CodeDialog';
const RadialbarChartsCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import Chart from 'react-apexcharts';
import { Grid }  from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Props } from 'react-apexcharts';


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

    return (
        <Chart
                options={optionsradialchart}
                series={seriesradialchart}
                type="radialBar"
                height="300px"
                />
    );
};

export default RadialbarChart;
`}
      </CodeDialog>
    </>
  );
};

export default RadialbarChartsCode;
