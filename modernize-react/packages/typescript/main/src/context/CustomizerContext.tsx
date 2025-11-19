
import { createContext, useState, ReactNode, useEffect } from 'react';
import config from './config'
import React from "react";

// Define the shape of the context state
interface CustomizerContextState {
    activeDir: string;
    setActiveDir: (dir: string) => void;
    activeMode: string;
    setActiveMode: (mode: string) => void;
    activeTheme: string;
    setActiveTheme: (theme: string) => void;
    activeLayout: string;
    setActiveLayout: (layout: string) => void;
    isCardShadow: boolean;
    setIsCardShadow: (shadow: boolean) => void;
    isLayout: string;
    setIsLayout: (layout: string) => void;
    isBorderRadius: number;
    setIsBorderRadius: (radius: number) => void;
    isCollapse: string;
    setIsCollapse: (collapse: string) => void;
    isSidebarHover: boolean;
    setIsSidebarHover: (isHover: boolean) => void;
    isMobileSidebar: boolean;  // Add this
    setIsMobileSidebar: (isMobileSidebar: boolean) => void
}

// Create the context with an initial value
export const CustomizerContext = createContext<CustomizerContextState | any>(undefined);

// Define the type for the children prop
interface CustomizerContextProps {
    children: ReactNode;
}
// Create the provider component
export const CustomizerContextProvider: React.FC<CustomizerContextProps> = ({ children }) => {

    const [activeDir, setActiveDir] = useState<string>(config.activeDir);
    const [activeMode, setActiveMode] = useState<string>(config.activeMode);
    const [activeTheme, setActiveTheme] = useState<string>(config.activeTheme);
    const [activeLayout, setActiveLayout] = useState<string>(config.activeLayout);
    const [isCardShadow, setIsCardShadow] = useState<boolean>(config.isCardShadow);
    const [isLayout, setIsLayout] = useState<string>(config.isLayout);
    const [isBorderRadius, setIsBorderRadius] = useState<number>(config.isBorderRadius);
    const [isCollapse, setIsCollapse] = useState<string>(config.isCollapse);
    const [isLanguage, setIsLanguage] = useState<string>(config.isLanguage);
    const [isSidebarHover, setIsSidebarHover] = useState<boolean>(false);
    const [isMobileSidebar, setIsMobileSidebar] = useState<boolean>(false);
    // Set attributes immediately
    useEffect(() => {
        document.documentElement.setAttribute("class", activeMode);
        document.documentElement.setAttribute("dir", activeDir);
        document.documentElement.setAttribute('data-color-theme', activeTheme);
        document.documentElement.setAttribute("data-layout", activeLayout);
        document.documentElement.setAttribute("data-boxed-layout", isLayout);
        document.documentElement.setAttribute("data-sidebar-type", isCollapse);

    }, [activeMode, activeDir, activeTheme, activeLayout, isLayout, isCollapse]);

    return (
        <CustomizerContext.Provider
            value={{

                activeDir,
                setActiveDir,
                activeMode,
                setActiveMode,
                activeTheme,
                setActiveTheme,
                activeLayout,
                setActiveLayout,
                isCardShadow,
                setIsCardShadow,
                isLayout,
                setIsLayout,
                isBorderRadius,
                setIsBorderRadius,
                isCollapse,
                setIsCollapse,
                isLanguage,
                setIsLanguage,
                isSidebarHover,
                setIsSidebarHover,
                isMobileSidebar,
                setIsMobileSidebar
            }}
        >
            {children}
        </CustomizerContext.Provider>
    );
};

