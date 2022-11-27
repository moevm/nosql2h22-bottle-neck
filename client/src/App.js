import './App.css';
import './index.css'
import * as React from 'react';
import ColorToggleButton from './components/toggle'
import InputComponent from "./components/inputComponent";
import {useEffect, useRef, useState} from "react";
function App(){

    const canvasRef = useRef(null);
    const contextRef = useRef(null);
    const [point1, point1State] = useState(null)
    const [point2, point2State] = useState(null)
    const [image, imageState] = useState(null)

    useEffect(() => {
        const canvas = canvasRef.current;
        canvas.width = 700;
        canvas.height = 700;
        const context = canvas.getContext("2d");
        context.lineCap = "round";
        context.strokeStyle = "blue";
        context.lineWidth = 8;
        let image_new = new Image()
        image_new.src = '/map_image'
        image_new.onload = function() {
            context.drawImage(image_new, 0, 0, 700, 700)
        }
        contextRef.current = context;
        imageState(image_new)
        /*fetch('/map_image')
            .then(response => response.blob())
            .then(imageBlob => {
                console.log(imageBlob)
                const imageURL = URL.createObjectURL(imageBlob);
                image.current.src = imageURL;
                console.log(image.current.src)
            })*/
    }, []);
    const startDrawing = ({nativeEvent}) => {
        const {offsetX, offsetY} = nativeEvent;
        console.log(offsetX, offsetY)
        if(point1 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point1State([offsetX, offsetY])
        }
        else if(point2 === null){
            contextRef.current.beginPath();
            contextRef.current.moveTo(offsetX, offsetY);
            contextRef.current.lineTo(offsetX, offsetY);
            contextRef.current.stroke();
            point2State([offsetX, offsetY])
        }
        console.log(point1, point2)

        nativeEvent.preventDefault();
    };
    function dropPoints(){
        console.log(5)
        contextRef.current.globalCompositeOperation = 'destination-out';
        contextRef.current.lineWidth=10
        if(point1 != null){
            contextRef.current.lineTo(point1[0], point1[1]);
            contextRef.current.stroke()
            point1State(null)
        }
        if(point2 != null){
            contextRef.current.lineTo(point2[0], point2[1]);
            contextRef.current.stroke()
            point2State(null)
        }
        contextRef.current.lineWidth=8
        contextRef.current.globalCompositeOperation = 'source-over';
        contextRef.current.drawImage(image, 0, 0, 700, 700)
    }

    return(
        <div className="App">
            <div className="right">
                <div className="inline">
                    <InputComponent value={0} label={"Количество машин"} type={"number"}
                                    onChange={() => console.log(1)}/>
                    <InputComponent value={false} label={"Радиус поиска маршрутов"} variant={"input"}
                                    type={"checkbox"}/>

                </div>
                <InputComponent vallue={0} type={"range"}/>
                <div className="inline">
                    <button>Смоделировать</button>
                    <button onClick={(e)=>{
                        dropPoints()
                        }}>Очистить точки на карте</button>
                </div>
                <p>Количество маршрутов: {6}</p>
                <br/>
                <ColorToggleButton/>
            </div>
            <div align="center">
                <div class="table">
                    <div class="row">
                        <div class="cell">
                            <canvas className="map"
                                    ref={canvasRef}
                                    onMouseDown={startDrawing}
                            >
                            </canvas>

                        </div>
                    </div>
                </div>
            </div>

        </div>
    )
}

export default App;
