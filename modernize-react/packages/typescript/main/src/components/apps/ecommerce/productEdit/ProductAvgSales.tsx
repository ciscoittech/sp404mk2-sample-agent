
import Chart from 'react-apexcharts';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import { Chip, Typography } from '@mui/material';

const ProductAvgSales = () => {
  const theme = useTheme();
  const primary = theme.palette.primary.main;

  // chart
  const optionsPrdAvgSaleschart: any = {
    chart: {
      type: 'bar',
      fontFamily: "'Plus Jakarta Sans', sans-serif;",
      foreColor: '#adb0bb',
      toolbar: {
        show: false,
      },
      height: 85,
      resize: true,
      barColor: '#fff',
      sparkline: {
        enabled: true,
      },
    },
    colors: [primary],
    grid: {
      show: false,
    },
    plotOptions: {
      bar: {
        horizontal: false,
        startingShape: 'flat',
        endingShape: 'flat',
        columnWidth: '60%',
        barHeight: '20%',
        borderRadius: 3,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 2.5,
      colors: ['rgba(0,0,0,0.01)'],
    },
    xaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        show: false,
      },
    },
    axisBorder: {
      show: false,
    },
    fill: {
      opacity: 1,
    },
    tooltip: {
      theme: theme.palette.mode === 'dark' ? 'dark' : 'light',
      x: {
        show: false,
      },
    },
  };
  const seriesPrdAvgSaleschart = [
    {
      name: '',
      data: [4, 10, 9, 7, 9, 10, 11, 8, 10],
    },
  ];

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight={500} mb={1}>
        $2,420
      </Typography>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="h6" fontSize="16px" fontWeight={400}>
          Average Daily Sales{' '}
        </Typography>
        <Chip size="small" color="success" label="2.6%" />
      </Box>

      <Box height="85px" mt={2}>
        <Chart
          options={optionsPrdAvgSaleschart}
          series={seriesPrdAvgSaleschart}
          type="bar"
          height={80}
          width={'100%'}
        />
      </Box>
    </Box>
  );
};

export default ProductAvgSales;
