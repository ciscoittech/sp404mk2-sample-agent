import CodeDialog from 'src/components/shared/CodeDialog';

function GaugePointerCode() {
  return (
    <CodeDialog>
      {`
import React from 'react'
import {
    GaugeContainer,
    GaugeValueArc,
    GaugeReferenceArc,
    useGaugeState,
} from '@mui/x-charts/Gauge';



const BCrumb = [
{
to: '/',
title: 'Home',
},
{
title: 'GaugePointerChart ',
},
]; 



function GaugePointer() {
    const { valueAngle, outerRadius, cx, cy } = useGaugeState();

    if (valueAngle === null) {
        // No value to display
        return null;
    }

    const target = {
        x: cx + outerRadius * Math.sin(valueAngle),
        y: cy - outerRadius * Math.cos(valueAngle),
    };
    return (
        <g>
            <circle cx={cx} cy={cy} r={5} fill="red" />
            <path
                d={\`M \${cx} \${cy} L \${target.x} \${target.y}\`}
            stroke="red"
            strokeWidth={3}
            />
        </g>
    );
}

export default function GaugePointerChart() {
    return (

        <GaugeContainer
            width={200}
            height={200}
            startAngle={-110}
            endAngle={110}
            value={30}
        >
            <GaugeReferenceArc />
            <GaugeValueArc />
            <GaugePointer />
        </GaugeContainer>
    );
}
`}
    </CodeDialog>
  );
}

export default GaugePointerCode;
